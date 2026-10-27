"""Credential-free regression gate. Run from repository root: python -m evals.run."""

import asyncio
import json
from pathlib import Path

from c4l.adapters import DemoAgent
from c4l.contracts import Limits
from c4l.engine import run
from c4l.policy import BaselinePolicy


async def main():
    results = []
    for line in Path("evals/cases.jsonl").read_text().splitlines():
        case = json.loads(line)
        result = await run(case["prompt"], DemoAgent(), BaselinePolicy(), Limits())
        results.append({"id": case["id"], "passed": result["status"] == case["status"]})
    print(json.dumps({"suite": "demo-regression-v1", "results": results}, indent=2))
    if not all(row["passed"] for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
