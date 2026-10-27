"""Synthetic paper-equation audit example; no claim about real agent quality or savings."""

import json

from c4l.ardc import ControllerConfig, DepthController
from c4l.contracts import DepthMeasurement


def main():
    config = ControllerConfig("synthetic-eq1-v1", "example-not-approved", 6, 0.0001, 0.9, 0.001, 2, 2)
    controller = DepthController(config)
    for n, mu in [(1, 1), (2, 0.25), (3, 0.25)]:
        row = controller.observe(DepthMeasurement(n, 4, 0.5, 1, -2, mu, config.protocol_id))
        if controller.stopped:
            break
    report = {
        "claim": "synthetic controller regression only",
        "config": config.__dict__,
        "audit": controller.audit,
        "selected_depth": row["selected_depth"],
    }
    print(json.dumps(report, indent=2, allow_nan=False))
    assert row["selected_depth"] == 2 and row["stop_reason"] == "diminishing_returns"


if __name__ == "__main__":
    main()
