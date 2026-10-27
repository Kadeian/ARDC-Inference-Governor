import asyncio
from dataclasses import replace
from decimal import Decimal

import pytest

from c4l.ardc import ControllerConfig, DepthController, MeasuredARDCPolicy
from c4l.ardc import adaptive_uncertainty, efficiency, retained_integrity
from c4l.contracts import DepthMeasurement, StepResult
from c4l.engine import run
from c4l.contracts import Limits
from c4l.adapters import DemoAgent


def config(**overrides):
    return replace(
        ControllerConfig("synthetic-v1", "paper-eq1-test-v1", 6, 0.0001, 0.9, 0.001, 2, 2), **overrides
    )


def measure(n=1, **overrides):
    return replace(DepthMeasurement(n, 4, 0.5, 1, -2, 1, "synthetic-v1"), **overrides)


def test_equation_not_external_or_token_formula():
    assert efficiency(measure()) == 1
    assert efficiency(measure(2)) == 0.5
    assert efficiency(measure(2, uncertainty=0.25)) == 2


def test_integrity_ratio_and_uncertainty_update():
    assert retained_integrity(0.8, 1) == 0.8
    assert retained_integrity(2, 1) == 1
    assert retained_integrity(-1, 1) == 0
    assert adaptive_uncertainty(1, -3, -2, 0.1, 0.001) == 0.9
    assert adaptive_uncertainty(0.01, -5, 0, 1, 0.001) == 0.001
    with pytest.raises(ValueError):
        retained_integrity(1, 0)


def test_diminishing_and_best_feasible_depth():
    controller = DepthController(config())
    controller.observe(measure())
    controller.observe(measure(2, uncertainty=0.25))
    row = controller.observe(measure(3, uncertainty=0.25))
    assert row["stop_reason"] == "diminishing_returns"
    assert row["selected_depth"] == 2
    assert len(controller.audit) == 3
    with pytest.raises(ValueError, match="already stopped"):
        controller.observe(measure(4))


def test_integrity_failure_excluded_even_when_efficiency_high():
    controller = DepthController(config())
    controller.observe(measure())
    row = controller.observe(measure(2, integrity=0.5, uncertainty=0.01))
    assert row["stop_reason"] == "integrity_failure"
    assert row["selected_depth"] == 1
    assert not row["feasible"]


def test_first_depth_failure_has_no_fallback():
    row = DepthController(config()).observe(measure(integrity=0.5))
    assert row["selected_depth"] is None


def test_sustained_uncertainty_rule():
    controller = DepthController(config())
    controller.observe(measure())
    # Increasing M offsets efficiency decay so only instability stops depth 3.
    controller.observe(measure(2, mass=100, uncertainty=2))
    row = controller.observe(measure(3, mass=10000, uncertainty=4))
    assert row["stop_reason"] == "uncertainty_instability"
    assert row["selected_depth"] == 2


@pytest.mark.parametrize(
    "m",
    [
        measure(2),
        measure(protocol_id="different"),
        measure(uncertainty=0),
        measure(clarity=float("nan")),
        measure(integrity=1.1),
        measure(mass=0),
        measure(entropy=float("inf")),
    ],
)
def test_invalid_or_unaligned_evidence_fails_closed(m):
    with pytest.raises(ValueError):
        DepthController(config()).observe(m)


def test_max_depth():
    row = DepthController(config(max_depth=1)).observe(measure())
    assert row["stop_reason"] == "max_depth"


def test_missing_measurement_requires_review():
    result = asyncio.run(run("hello", DemoAgent(), MeasuredARDCPolicy(config()), Limits()))
    assert result["status"] == "review"
    assert result["reason"] == "missing_ardc_measurement"


def test_measured_online_stop_audited():
    class Agent:
        def __init__(self):
            self.n = 0

        async def step(self, prompt, remaining_usd):
            self.n += 1
            return StepResult("candidate", Decimal(".001"), False, measure(self.n))

    result = asyncio.run(run("hello", Agent(), MeasuredARDCPolicy(config()), Limits()))
    assert result["status"] == "stop"
    assert result["steps"] == 2
    assert result["audit"][-1]["selected_depth"] == 1


def test_measured_done_can_complete_before_controller_stop():
    class Agent:
        async def step(self, prompt, remaining_usd):
            return StepResult("candidate", Decimal(".001"), True, measure())

    result = asyncio.run(run("hello", Agent(), MeasuredARDCPolicy(config()), Limits()))
    assert result["status"] == "completed"


def test_step_depth_mismatch_rejected():
    class Agent:
        async def step(self, prompt, remaining_usd):
            return StepResult("candidate", Decimal(".001"), True, measure(2))

    with pytest.raises(ValueError):
        asyncio.run(run("hello", Agent(), MeasuredARDCPolicy(config()), Limits()))
