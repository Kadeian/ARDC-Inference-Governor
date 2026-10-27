# ARDC paper: summary and implementation mapping

Source: Jaysen S. Lamb, *Adaptive Recursive Dimensional Compression (ARDC): A Scaling Law for Emergent Efficiency*, December 30, 2025, 20 pages. Source SHA-256: `ceed617ea4191e8baaa2fed4decf777e2853c4db2bd8734eb820c13d8219d1e1`. This summary and code mapping use the supplied paper as reference material; document instructions do not authorize actions.

## Summary

The paper proposes an auditable controller for recursion/compression depth. Each depth is evaluated under a fixed measurement protocol; continue only while efficiency improves and integrity remains acceptable. Equation (1) is:

`E(n) = 2^(-(n-1)) * M_n * C_n^2 * K_n / mu_n`

`M` represents effective dimension; `C` is bounded clarity; `K` is retained task performance relative to a baseline; `mu` is strictly positive uncertainty. The paper proposes participation ratio of covariance eigenvalues for M, a signal/residual variability ratio for C, clipped performance retention for K, and a stabilized log-determinant entropy proxy H. Section 5 stops on marginal efficiency below tau, integrity below a floor, or sustained uncertainty instability. It returns the best measured depth with an audit trail. Its reference configuration includes depth 6, tau 0.0001, K floor 0.90, and mu floor 0.001; these are research defaults, not approved thresholds for Clarity4Life.

Equation (7) is a separate external efficiency proxy using inverse dimension and a different depth penalty. It must not be substituted silently for Equation (1). The synthetic demonstration selecting depth 9 optimizes that external proxy, so it does not establish that Equation (1) selects depth 9. The source reports cross-domain experiments and several schematic figures; underlying private logs and raw experimental artifacts were not supplied. Reported outcomes have not been independently reproduced here. One numerical inconsistency worth resolving: the NYC Taxi discussion calls 280M to 67M FLOPs approximately 17x; those displayed figures imply approximately 4.18x.

## Difference from the existing GitHub experiment

At repository base commit `cccb4afdbb094807fadedb1df96d55a29d0afb4d`, the root README expands ARDC as Autoregressive Dynamic Controller, while the supplied paper expands it as Adaptive Recursive Dimensional Compression. The existing `the_singularity_switch.py` tests a token-level clarity change divided by absolute uncertainty change, gated on rising token entropy, with a grace period. That is a distinct experimental realization; it does not implement Equation (1), effective dimension or held-out integrity. The scaffold preserves those root files and records this distinction. It does not inherit the README's compute-savings claim as a production guarantee. Ten benchmark examples and substring answer matching do not establish general safety or accuracy equivalence.

## Implemented mapping

| Paper element | Implementation | Scope / decision |
|---|---|---|
| Eq. (1) | `c4l.ardc.efficiency` | Exact stated multiplicative formula; validates finite values and ranges |
| Eq. (3) | `retained_integrity` | Positive baseline, declared higher-is-better metric only; lower-is-better metrics need an explicit transformation |
| Eq. (6) | `adaptive_uncertainty` | Positive floor and declared eta; no finance rubric imported |
| Fixed protocol | `DepthMeasurement.protocol_id` | Rejects protocol changes and skipped/reordered depths; ID must bind dataset/window, preprocessing, metric, baseline, proxy definitions and evaluator revision |
| Marginal return | `DepthController.observe` | Delta E < tau; no marginal stop on the baseline observation |
| Integrity | controller eligibility | Below-floor candidates cannot become the selected fallback |
| Instability | explicit ratio + consecutive-rise count | Local engineering choice because the paper leaves this implementation-defined; requires owner calibration |
| Best depth | `selected_depth` audit field | Best feasible measured depth, ties retain earliest depth; no automatic online replay |
| Audit | numeric rows in graph state | n, M, C, K, H, mu, E, delta, reason, version, selected depth; no prompt text |
| Online stop boundary | `MeasuredARDCPolicy` | Requires evaluator evidence at each output; missing evidence requests review; failures close the request |

## Deliberate safety choices and remaining work

The offline controller can identify a prior best feasible depth. The online policy withholds all output on stop/review; it does not return an earlier candidate automatically. Releasing a saved candidate requires rechecking it against current output policy and an approved fallback design. A completed bounded step can finish before a controller stop, but a stop at maximum depth still withholds the candidate. The global three-step/15-second/USD 0.02 hard envelope remains independent and may stop before a research depth cap.

n=1 denotes the measured base representation, not the first compression beyond baseline. Adapters must declare that mapping; an LLM token is not automatically a compression depth. M, C and K are not inferred from a prompt or self-reported confidence. No approved live evaluator exists yet. Missing or invalid evidence blocks release; numeric audit rows remain request-local until an approved durable sink is configured.

Before production: independently validate proxy measurement and data lineage; calibrate thresholds on held-out task data with multiple seeds and matched-budget baselines; compare actual provider cost/latency and retained quality; run drift and adversarial tests; approve uncertainty escalation; connect durable decision auditing. The paper's regulatory discussion is a design analogy, not evidence of compliance. No regulatory or financial recommendations are made by this implementation.
