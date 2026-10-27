# Validation record

Executed locally on October 27, 2026:

- 10 pytest tests passed: normal graph, blocked input never invokes agent, output guard, step cap, cost overrun/invalid usage, policy outage, deadline, explicit review, API auth/validation/withholding, and live demo rejection.
- 3 deterministic evaluation cases passed: normal, injection indicator and possible secret.
- Ruff configured lint checks passed; Python sources formatted.
- Terraform 1.10.5 formatting and validation passed with AWS provider 6.70.0. Provider checksum lock included.

The local dependency set included FastAPI 0.162.0, LangGraph 1.2.18, pytest 9.1.1 and httpx 0.28.1. Dependency bounds in pyproject remain intentionally broad for this initial scaffold; create and audit a hash-locked release environment before deployment. Local tests ran in a workspace-only dependency directory. No cloud credentials or model provider calls were used.

Not executed: Docker build/Compose (Docker unavailable), full CI/dependency audit/container scans, Terraform plan/apply (no AWS access requested), actual agent or proprietary ARDC integration, quality evaluation against domain data, real telemetry exporter integration, live canary and rollback. Terraform validation checks provider schema and local consistency; it cannot prove account permissions, quotas, network reachability or runtime behavior.

Treat all production gaps in PLAN.md as release blockers. This record establishes a tested initial scaffold, not production readiness.

## Paper-integration increment

On the same date, 14 new numeric/controller tests passed and 4 new async integration tests were collected but could not run locally: this restricted Windows runner stalls creating Python asyncio's loopback socketpair. The expanded full suite is therefore delegated to the GitHub pull request CI. The synthetic `evals.ardc_run` audit passed, selecting depth 2 then stopping on diminishing return at depth 3. Ruff passes on the updated source. Earlier 10 passing tests describe the baseline before this increment; they are not a claim that all updated async paths were locally rerun. No model/provider access or AWS deployment occurred.
