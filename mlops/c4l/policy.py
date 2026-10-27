import re

from c4l.contracts import Decision, PolicyContext


class BaselinePolicy:
    """Demonstration guardrails, not a complete safety classifier or approved ARDC policy."""

    async def evaluate(self, context: PolicyContext) -> Decision:
        reason = "allowed"
        action = "allow"
        if context.spent_usd >= context.limits.max_cost_usd:
            action, reason = "stop", "budget_exhausted"
        elif context.phase == "before_step" and context.steps >= context.limits.max_steps:
            action, reason = "stop", "step_limit"
        elif re.search(r"\b(sk-[A-Za-z0-9_-]{12,}|AKIA[A-Z0-9]{16})\b", context.text):
            action, reason = "stop", "possible_secret"
        elif re.search(r"ignore (all |previous )?instructions", context.text, re.I):
            action, reason = "review", "injection_indicator"
        elif len(context.text) > 8000:
            action, reason = "stop", "text_limit"
        return Decision(action, reason, "baseline-demo-v1")
