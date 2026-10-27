from decimal import Decimal

from c4l.contracts import StepResult


class DemoAgent:
    async def step(self, prompt: str, remaining_usd: Decimal) -> StepResult:
        return StepResult("Demo agent connected. Configure a reviewed Clarity4Life adapter.", Decimal("0"))


def load_factory(path: str):
    """Operator-controlled module:factory; never accepted from HTTP input."""
    import importlib

    module, name = path.split(":", 1)
    return getattr(importlib.import_module(module), name)
