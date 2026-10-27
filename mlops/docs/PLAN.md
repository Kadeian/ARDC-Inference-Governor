# Current product scope

The first product is a NEW Workforce Benefits Navigator for Texas adults, replacing the original existing-agent selection step. See WORKFORCE_NAVIGATOR.md for current scope, boundaries and delivery phases. Earlier infrastructure phases below continue to apply where relevant. No existing proprietary agent is required.

# Phased implementation and gates

This repository is an initial scaffold, not a deployed or certified production service. The supplied ARDC paper has been summarized and mapped to a numeric reference controller. No live agent integration, provider access, approved measurement protocol, or NVIT roster was supplied. Demo behavior cannot be enabled in a live environment. The sponsor owns approval; students cannot approve their own production release.

| Phase | Work and owner | Exit evidence |
|---|---|---|
| 0: discovery | Architecture lead: identify one Clarity4Life agent, intended users, data classification, risk boundaries, ARDC owner, provider/model and approved region | Signed agent inventory, policy specification, threat model, budget and data-retention decision |
| 1: local baseline | API/governance workstreams: adapter, graph, auth, bounds, guardrails | CI tests and demo evals pass; no credentials needed |
| 2: real integration | Agent owner: request-scoped bounded adapter; governance owner: versioned ARDC implementation | Contract tests, provider cancellation/usage reconciliation, zero ungoverned tool calls, fail-closed fault injection |
| 3: quality/security | Evaluation and platform workstreams | Approved, de-identified domain corpus; 100% critical safety cases; measured quality floor; zero unresolved critical/high findings; load and tenant isolation tests |
| 4: restricted AWS staging | Platform lead | Reviewed Terraform plan and cost estimate; private networking; secret rotation; staging smoke/load tests; trace export; budget alarms; rollback drill |
| 5: production canary | Sponsor + policy + platform owners | Approved evidence URL; protected GitHub environment; 10%/5-minute canary with synthetic traffic; automatic alarm rollback demonstrated |
| 6: operation | Rotation owned by named staff | SLO review, drift checks, usage reconciliation, incident exercise and handoff |

Initial proposed SLOs (approve after staging measurement): p95 < 5 seconds, execution failures < 1%, no critical policy leaks, no unknown billing events during release. Low traffic must use synthetic requests; a quiet alarm is not evidence of correctness. Monitor 30 minutes after promotion.

## Evaluation progression

`python -m evals.run` is a deterministic regression gate for the demo, not a quality claim for the existing agent. Replace/add versioned labeled cases for correctness, refusal, injection, sensitive data, grounding and tool authorization. Evaluate the real adapter with an explicit opt-in staging runner and isolated provider budget. Human experts approve critical outcomes. For RAG agents, add retrieval relevance and evidence-supported answers (RAGAS or an equivalent evaluator); never send private reference data to an external judge without approval. Store dataset hash, model/provider revision, adapter commit, policy version, per-case outcome, latency and usage in release evidence. Block release on any critical failure and on statistically material regression against the approved baseline.

## Known production gaps, all deployment blockers

Real adapter and ARDC policy; approved domain eval corpus; dependency/base-image digest locks and vulnerability review; per-user authentication/authorization and distributed rate/budget enforcement; request byte limits at the edge; WAF and abuse controls; durable audit retention; AWS OTEL collector and Prometheus scrape/auth integration; provider billing reconciliation; production-specific latency/availability alarms; verified DNS/TLS and website backend integration. The local shared API token is for a trusted backend only and must never be embedded in browser code. No DNS or clarity4life.net changes are made by this scaffold.

## Paper integration increment

Added exact Equation (1) depth scoring, finite/range and protocol checks, integrity and instability stops, best feasible depth audit, and a measured LangGraph policy bridge. The paper's reference thresholds are illustrative; independent calibration, real evaluator integration, numeric audit persistence and fallback approval remain Phase 2/3 gates. Preserve a distinction from the repository's existing token-level experiment.
