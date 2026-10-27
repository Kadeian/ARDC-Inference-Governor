"""Paper-derived Eq. (1) controller; proxies/configuration require validation.

Source: Lamb, Adaptive Recursive Dimensional Compression, 2025-12-30,
Sections 3-5. Does not substitute external-efficiency or token-level formulas.
"""

import math
from dataclasses import asdict, dataclass

from c4l.contracts import Decision, DepthMeasurement, PolicyContext
from c4l.policy import BaselinePolicy


@dataclass(frozen=True)
class ControllerConfig:
    protocol_id: str
    policy_version: str
    max_depth: int
    tau: float
    integrity_floor: float
    mu_min: float
    # Explicit local realization of the paper's implementation-defined rule.
    instability_ratio: float
    instability_patience: int

    def __post_init__(self):
        values = (self.tau, self.integrity_floor, self.mu_min, self.instability_ratio)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Non-finite controller configuration")
        if (
            not self.protocol_id
            or not self.policy_version
            or self.max_depth < 1
            or self.tau <= 0
            or not 0 <= self.integrity_floor <= 1
            or self.mu_min <= 0
            or self.instability_ratio <= 1
            or self.instability_patience < 1
        ):
            raise ValueError("Invalid controller configuration")


def efficiency(m: DepthMeasurement) -> float:
    """E(n) = 2**(-(n-1)) * M * C**2 * K / mu, dimensionless."""
    values = (m.mass, m.clarity, m.integrity, m.entropy, m.uncertainty)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Non-finite measurement")
    if (
        m.n < 1
        or m.mass < 1
        or not 0 < m.clarity <= 1
        or not 0 <= m.integrity <= 1
        or m.uncertainty <= 0
        or not m.protocol_id
    ):
        raise ValueError("Invalid measurement")
    value = math.ldexp(1.0, -(m.n - 1)) * m.mass * m.clarity**2 * m.integrity / m.uncertainty
    if not math.isfinite(value):
        raise ValueError("Non-finite efficiency")
    return value


def retained_integrity(score: float, baseline_score: float) -> float:
    """Eq. (3) for a declared higher-is-better metric with positive baseline."""
    if not all(math.isfinite(v) for v in (score, baseline_score)) or baseline_score <= 0:
        raise ValueError("Positive finite baseline required")
    return min(1.0, max(0.0, score / baseline_score))


def adaptive_uncertainty(
    previous_mu: float, entropy: float, previous_entropy: float, eta: float, mu_min: float
) -> float:
    """Eq. (6); all parameters belong to the declared measurement protocol."""
    if not all(math.isfinite(v) for v in (previous_mu, entropy, previous_entropy, eta, mu_min)):
        raise ValueError("Non-finite uncertainty input")
    if previous_mu <= 0 or eta < 0 or mu_min <= 0:
        raise ValueError("Invalid uncertainty input")
    result = max(mu_min, previous_mu + eta * (entropy - previous_entropy))
    if not math.isfinite(result):
        raise ValueError("Non-finite updated uncertainty")
    return result


class DepthController:
    """Request-scoped audit; selection excludes integrity/instability failures.

    n=1 is the measured base representation. Observations must be consecutive.
    The adapter declares how bounded steps correspond to measured depths.
    """

    def __init__(self, config: ControllerConfig):
        self.config = config
        self.audit: list[dict] = []
        self.best: dict | None = None
        self.rising = 0
        self.stopped = False

    def observe(self, m: DepthMeasurement) -> dict:
        if self.stopped:
            raise ValueError("Controller already stopped")
        if m.protocol_id != self.config.protocol_id or m.n != len(self.audit) + 1:
            raise ValueError("Protocol drift or nonconsecutive depth")
        if m.uncertainty < self.config.mu_min:
            raise ValueError("Uncertainty below configured floor")
        value = efficiency(m)
        previous = self.audit[-1] if self.audit else None
        delta = value - previous["efficiency"] if previous else None
        if previous and m.uncertainty >= previous["uncertainty"] * self.config.instability_ratio:
            self.rising += 1
        else:
            self.rising = 0
        reason = "continue"
        feasible = True
        if m.integrity < self.config.integrity_floor:
            reason, feasible = "integrity_failure", False
        elif self.rising >= self.config.instability_patience:
            reason, feasible = "uncertainty_instability", False
        elif delta is not None and delta < self.config.tau:
            reason = "diminishing_returns"
        elif m.n >= self.config.max_depth:
            reason = "max_depth"
        row = {
            **asdict(m),
            "efficiency": value,
            "delta_efficiency": delta,
            "feasible": feasible,
            "stop_reason": reason,
            "policy_version": self.config.policy_version,
        }
        if feasible and (self.best is None or value > self.best["efficiency"]):
            self.best = row.copy()
        row["selected_depth"] = self.best["n"] if self.best else None
        self.audit.append(row)
        self.stopped = reason != "continue"
        return row.copy()


class MeasuredARDCPolicy:
    """Conservative online bridge; stop/review withholds text, no automatic fallback.

    Construct through an operator-owned factory with approved config and guardrails.
    Baseline guardrails are illustrative and must be replaced before deployment.
    """

    def __init__(self, config: ControllerConfig, guardrails=None):
        self.controller = DepthController(config)
        self.guardrails = guardrails if guardrails is not None else BaselinePolicy()

    async def evaluate(self, context: PolicyContext) -> Decision:
        gate = await self.guardrails.evaluate(context)
        if gate.action != "allow":
            return gate
        version = self.controller.config.policy_version
        if context.phase != "output":
            return Decision("allow", "await_measurement", version)
        if context.measurement is None:
            return Decision("review", "missing_ardc_measurement", version)
        if context.measurement.n != context.steps:
            raise ValueError("Measurement does not match executed depth")
        row = self.controller.observe(context.measurement)
        action = "stop" if self.controller.stopped else "allow"
        return Decision(action, row["stop_reason"], version, row)
