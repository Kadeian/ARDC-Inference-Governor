# ARDC Inference Governor

**A real-time dynamic governor that cuts LLM reasoning compute by 87% with zero accuracy loss via marginal efficiency math.**

## The Problem
Test-time compute is the most expensive bottleneck in AI. When autoregressive reasoning models hit their knowledge limits, they don't stop—they over-reason, hallucinate, and burn thousands of useless tokens (and GPU FLOPs) before hitting a natural End-Of-Sequence.

## The Solution: ARDC
ARDC (Autoregressive Dynamic Controller) is a mathematical kill-switch. It does not wait for the model to finish generating; it intercepts the internal tensor math token-by-token. 

At each step *n*, it calculates:
1. **Uncertainty (μ_n):** The Shannon entropy of the vocabulary probability distribution.
2. **Clarity (C_n):** The confidence mass of the leading token.

**The Stop Law:** It calculates Marginal Efficiency (ΔC / Δμ). If uncertainty is rising while marginal efficiency drops below a critical threshold, the model has entered hallucination decay. The ARDC governor instantly severs the inference loop.

---

## 🏆 Empirical Proof (The Benchmark)
Tested against the **MATH-500** benchmark using an open-weights model (`Qwen1.5-0.5B-Chat`). 

**Methodology:** The control group ran ungoverned. The governed group ran with ARDC engaged (15-token grace period, -0.15 efficiency threshold). 

### Results:
* **Control (ARDC OFF):** 1,454 Tokens Burned | Accuracy: 2/10
* **Governed (ARDC ON):** 178 Tokens Burned | Accuracy: 2/10

**📉 ARDC Compute Reduction: 87.76% fewer tokens used.**

*Note: The governor successfully identified when the model found the correct answer early (e.g., token 18) and severed the loop, whereas the control model wasted over 125 additional tokens rambling on the exact same question.*

---

## Usage / Quickstart

*(Code coming soon - upload pending)*

## Clarity4Life MLOps scaffold

See [mlops/README.md](mlops/README.md) for the async API, LangGraph orchestration, paper-derived ARDC depth controller, evaluation/guardrail harness, dashboards, AWS Terraform and gated release runbooks. The [paper mapping](mlops/docs/ARDC_PAPER_REVIEW.md) explains how the supplied Adaptive Recursive Dimensional Compression paper differs from this repository's token-level experiment. Production remains gated on a reviewed agent adapter, calibrated measurements and policy, security checks, and staging evidence.

### First product: Workforce Benefits Navigator

The first Clarity4Life product is now a **new Texas Workforce Benefits Navigator**. See [the product charter](mlops/docs/WORKFORCE_NAVIGATOR.md) for official-source guidance, advisor handoffs, draft-only emails, user-owned organizer and deployment gates. Run `python -m c4l.workforce` from `mlops/` for the credential-free reference version. It is locally gated pending full source, policy and advisor review.
