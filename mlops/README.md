# Clarity4Life MLOps and governance

Initial production-oriented scaffold and NEW Texas Workforce Benefits Navigator for Clarity4Life. Runs without provider credentials using a deterministic demo. Live startup rejects the demo agent and baseline policy. Nothing has been deployed and no website changes have been made.

## Run locally

Use Python 3.12:

```sh
python -m venv .venv
# Activate .venv for your shell, then:
pip install -e '.[dev]'
# Set API_TOKEN to at least 32 random characters in your environment.
uvicorn c4l.api:app --no-access-log
pytest -q
python -m evals.run
```

POST `/v1/agent` with `Authorization: Bearer <API_TOKEN>` and JSON `{"prompt":"Help me plan a study session"}`. Responses include status, policy version, reason, steps, reported cost and a server-generated request ID. Only completed responses expose candidate text. `/health/live` and `/health/ready` are public; `/metrics` requires authentication. Readiness currently confirms startup only, not provider connectivity.

For containers, copy `.env.example` to `.env`, set a random API token and `GRAFANA_PASSWORD`, and create `observability/metrics-token` containing the same API token (one line). Run `docker compose up --build`. API, Prometheus and Grafana bind to localhost at ports 8000, 9090 and 3000. Grafana username is `admin`. Keep local metrics and dashboards private. Review/pin current image digests before shared use.

## Structure

| Path | Purpose |
|---|---|
| `c4l/contracts.py` | Bounded agent and ARDC policy interfaces |
| `c4l/engine.py` | LangGraph input → pre-step → agent → output gates |
| `c4l/api.py` | Async authenticated FastAPI service |
| `tests/`, `evals/` | Fault tests and deterministic regression gate |
| `observability/` | Prometheus metrics, Grafana dashboard and optional OTLP spans |
| `infra/` | Restricted AWS ECS/Fargate, TLS ALB, ECR, secrets references, budget and CodeDeploy |
| `.github/workflows/` | CI checks and manually gated release dispatch |
| `docs/` | Phased plan, contracts, security/deployment gates, team workstreams and runbooks |

Start with [the implementation plan](docs/PLAN.md), [adapter and ARDC contract](docs/ADAPTER_AND_ARDC.md), [paper review and implementation mapping](docs/ARDC_PAPER_REVIEW.md), and [deployment runbook](docs/OPERATIONS.md). Production blockers are listed explicitly in the plan. No provider keys, AWS account assumptions, ARDC rules or existing agent implementations are invented.

## Sources

Architecture follows the [LangGraph graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [AWS ECS CodeDeploy deployment model](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-steps-ecs.html), and [GitHub AWS OIDC guidance](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws). Provider schemas must be validated against the pinned Terraform provider before deployment.

## Paper-derived ARDC extension

`c4l/ardc.py` implements Equation (1), retained integrity, adaptive uncertainty, audited depth selection, and a measured online policy. Run `python -m evals.ardc_run` for a synthetic numeric audit. The real adapter must supply trusted `DepthMeasurement` evidence and an approved versioned measurement protocol. Missing evidence requests review. This is a reference implementation, not a claim that the existing agent has been validated or that its token-level governor is equivalent. See the paper review for differences and deployment gates.

## Workforce Benefits Navigator

The first product is a new agent for Texas adults navigating unemployment and training funding. Run `python -m c4l.workforce` for the credential-free interactive source-card assistant. API routes: `/v1/navigator` and `/v1/navigator/organizer`. Run `python -m evals.workforce_run` for its synthetic safety gate. See [the product charter](docs/WORKFORCE_NAVIGATOR.md) for source limitations, advisor handoffs, user-owned tracking, ARDC integration and launch gates. No model credentials or personal client records are required.
