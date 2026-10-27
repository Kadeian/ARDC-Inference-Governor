import asyncio
from decimal import Decimal
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from opentelemetry import trace

from c4l.contracts import AgentAdapter, ARDCPolicy, DepthMeasurement, Limits, PolicyContext

tracer = trace.get_tracer(__name__)


class State(TypedDict):
    prompt: str
    candidate: str
    steps: int
    cost: Decimal
    status: str
    reason: str
    policy_version: str
    done: bool
    measurement: DepthMeasurement | None
    audit: list[dict]


async def run(prompt: str, adapter: AgentAdapter, policy: ARDCPolicy, limits: Limits) -> State:
    state: State = dict(
        prompt=prompt,
        candidate="",
        steps=0,
        cost=Decimal(0),
        status="running",
        reason="",
        policy_version="",
        done=False,
        measurement=None,
        audit=[],
    )

    async def check(s, phase, text):
        with tracer.start_as_current_span("governance." + phase):
            decision = await policy.evaluate(
                PolicyContext(phase, text, s["steps"], s["cost"], limits, s["measurement"])
            )
        if decision.action not in {"allow", "stop", "review"} or not decision.policy_version:
            raise ValueError("Invalid policy decision")
        return dict(
            status="running" if decision.action == "allow" else decision.action,
            reason=decision.reason_code,
            policy_version=decision.policy_version,
            audit=s["audit"] + ([decision.audit] if decision.audit is not None else []),
        )

    async def input_gate(s):
        return await check(s, "input", s["prompt"])

    async def before(s):
        # Hard limits are independent of the pluggable ARDC policy.
        if s["steps"] >= limits.max_steps or s["cost"] >= limits.max_cost_usd:
            return dict(status="stop", reason="hard_limit")
        return await check(s, "before_step", s["prompt"])

    async def step(s):
        with tracer.start_as_current_span("agent.step"):
            result = await adapter.step(s["prompt"], limits.max_cost_usd - s["cost"])
        if not result.cost_usd.is_finite() or result.cost_usd < 0:
            raise ValueError("Invalid usage")
        cost = s["cost"] + result.cost_usd
        return dict(
            candidate=result.text,
            cost=cost,
            steps=s["steps"] + 1,
            done=result.done,
            measurement=result.measurement,
            status="stop" if cost > limits.max_cost_usd else "running",
            reason="budget_overrun" if cost > limits.max_cost_usd else "",
        )

    async def output_gate(s):
        result = await check(s, "output", s["candidate"])
        if result["status"] == "running" and s["done"]:
            result["status"] = "completed"
        return result

    graph = StateGraph(State)
    for name, node in [("input", input_gate), ("before", before), ("step", step), ("output", output_gate)]:
        graph.add_node(name, node)
    graph.add_edge(START, "input")
    graph.add_conditional_edges("input", lambda s: "before" if s["status"] == "running" else END)
    graph.add_conditional_edges("before", lambda s: "step" if s["status"] == "running" else END)
    graph.add_conditional_edges("step", lambda s: "output" if s["status"] == "running" else END)
    graph.add_conditional_edges("output", lambda s: "before" if s["status"] == "running" else END)
    async with asyncio.timeout(limits.timeout_seconds):
        return await graph.compile().ainvoke(state, {"recursion_limit": limits.max_steps * 4 + 8})
