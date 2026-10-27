from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Protocol


@dataclass(frozen=True)
class Limits:
    max_cost_usd: Decimal = Decimal("0.02")
    max_steps: int = 3
    timeout_seconds: float = 15


@dataclass(frozen=True)
class DepthMeasurement:
    """Trusted evaluator output under a fixed protocol; never user assertions."""

    n: int
    mass: float
    clarity: float
    integrity: float
    entropy: float
    uncertainty: float
    protocol_id: str


@dataclass(frozen=True)
class StepResult:
    text: str
    cost_usd: Decimal
    done: bool = True
    measurement: DepthMeasurement | None = None


class AgentAdapter(Protocol):
    """One bounded step. No hidden retries, tools, background work, or unmetered calls.

    Adapter must enforce the supplied remaining budget BEFORE provider dispatch,
    cap tokens/tool calls, honor cancellation, and report all billable usage.
    Carry continuation state in an adapter instance created per request.
    """

    async def step(self, prompt: str, remaining_usd: Decimal) -> StepResult: ...


@dataclass(frozen=True)
class PolicyContext:
    phase: Literal["input", "before_step", "output"]
    text: str
    steps: int
    spent_usd: Decimal
    limits: Limits
    measurement: DepthMeasurement | None = None


@dataclass(frozen=True)
class Decision:
    action: Literal["allow", "stop", "review"]
    reason_code: str
    policy_version: str
    audit: dict | None = None


class ARDCPolicy(Protocol):
    """Integration contract only; the scaffold does not define proprietary ARDC semantics.

    All phases require explicit allow. Exceptions, unknown decisions, stop, and
    review withhold output. Review does not resume automatically.
    """

    async def evaluate(self, context: PolicyContext) -> Decision: ...
