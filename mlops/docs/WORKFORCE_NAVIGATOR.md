# Workforce Benefits Navigator: product charter

Build a NEW Clarity4Life agent for laid-off and underemployed adults in Texas. Career advisors are the secondary audience. The goal is to help people prepare for an advisor-confirmed path to training; funding, eligibility and employment are never promised. No existing agent is required. The application must not claim that the assistant has personally experienced the benefits process.

## First version

This is a credential-free, deterministic source-card assistant. It explains the unemployment/training tracks, work-search recordkeeping, employment plans, financial-literacy services, local cost-quote/bid-letter questions, training-program checks and advisor meeting preparation. It drafts placeholder emails for the user to review and send. It offers a stateless organizer for actual weekly activities, user-entered deadlines and document-status checkboxes.

Run `python -m c4l.workforce` for the interactive local version. Authenticated API routes: POST `/v1/navigator` with `question` and optional `state` (default TX); POST `/v1/navigator/organizer` with Sunday `week_start`, work-search entries, deadlines and document-status booleans. See tests/test_workforce.py for synthetic examples. No model/provider credentials are needed.

The organizer returns a record for the caller to save. It does not remember previous weeks, send reminders, upload documents, certify qualifying activities or replace all fields on TWC's official log. A user-owned interface/export workflow is a next increment; this is not yet a complete persistent tracking product.

## Boundaries

- Texas only. Regional Workforce Solutions examples are explicitly labeled.
- No eligibility decisions: TWC determines unemployment; authorized local program staff determine WIOA services/funding. The agent prepares questions for them.
- Official TWC, DOL and Workforce Solutions references in every answer. Unknown, stale or unsupported questions hand off rather than guess.
- No SSNs, bank details or identification numbers requested or stored. Conservative input checks refuse likely identifiers without echoing them. Checks are incomplete heuristics and need adversarial review before public launch.
- No server conversation history, database, attachments or third-party model calls. Request bodies exist transiently in transport and memory; disable raw body capture in proxies/APM. Validation errors do not echo rejected inputs.
- No sending, filing, submitting or applications on the user's behalf. Draft text contains placeholders and is never sent automatically.
- No legal or financial advice. Disputes, denials, hearings and overpayments stop and refer to a person; no appeal deadline is invented.
- Crisis indicators interrupt workforce tasks and ask for immediate human support. Phrase matching is not a crisis classifier. A reviewed crisis-escalation path is a public-launch gate; no unverified hotline is embedded.

## Process distinctions

TWC unemployment requirements and WIOA training funding are separate tracks. Employment plans are individualized. Financial literacy may be a service, but the reviewed material does not establish a mandatory class for every Texas adult. No universal bid-letter process was established. Ask the local advisor for the actual required tasks, formats, secure document channels and dates. An ETPL listing is not an individual's funding award; this version does not perform live provider-status lookup. An advisor email does not replace required TWC reporting.

## ARDC stopping interface

NavigatorStopPolicy implements the existing ARDCPolicy allow/stop/review contract. In this deterministic slice, confidence means a binary evidence gate: in-scope source card, source age within the declared limit, and an output exactly matching the vetted template. It is not a probability estimate. Missing evidence and scope mismatches hand off. Unsupported output is withheld. No user text is needed in graph state after preflight.

The paper's Equation (1) numeric controller remains separately available in c4l/ardc.py. No M/C/K/mu values are fabricated to claim it governs this agent. Before adding model-driven retrieval/refinement, establish trusted measurements, map iterations to depth, calibrate uncertainty and integrity, and compare against this deterministic baseline. Public deployment remains gated on that domain validation and the existing security/deployment checks.

## Official source register

Consulted October 27, 2026. Direct TWC requests encountered JavaScript/403 barriers; these initial cards use official indexed excerpts. Full document snapshots, supersession checks and local-advisor review remain mandatory before public use. The 30-day freshness gate is an engineering default, not an official requirement; age alone cannot establish correctness.

- TWC Unemployment Benefits Handbook: https://www.twc.texas.gov/sites/default/files/ui/docs/unemployment-benefits-handbook-twc.pdf
- TWC WIOA Guidelines, August 2025: https://www.twc.texas.gov/sites/default/files/wf/docs/wioa-guidelines-twc.pdf
- TWC statewide ETPL policy update: https://www.twc.texas.gov/policy-letters/statewide-eligible-training-providers-list-update
- DOL Adult and Dislocated Worker overview: https://www.dol.gov/agencies/eta/workforce-investment/adult
- Gulf Coast training scholarships, regional example only: https://www.wrksolutions.com/job-seekers/career-development-and-training/training-and-education-scholarships

Reference links on safety handoffs are workforce contact starting points, not proof of internal privacy rules or crisis-care recommendations.

## Delivery phases and NVIT workstreams

1. Current: source cards, boundaries, drafts, stateless organizer and synthetic safety regression.
2. Governance/evaluation: select a Texas pilot area, review complete source snapshots and local procedures, obtain staff policy-owner signoff, expand adversarial and multilingual tests.
3. Product/API: accessible user-owned checklist/log interface and export, deadline provenance, advisor-meeting workflow. Define consent/retention before persistence.
4. Agent integration: optional budgeted language-model layer with source attribution and calibrated ARDC measurements; request provider access only when implementation needs it.
5. Platform/reliability: restricted AWS staging, user auth, abuse controls, source-refresh and escalation drills, observability, canary and rollback.
6. Public Texas launch: independent domain/security/privacy review, tested crisis path, incident ownership and approved release evidence.

Proposed outcome measures are completed steps, confirmed deadlines missed, meeting readiness and elapsed time from job loss to confirmed funding/training start. These require consented, minimized event data with clear denominators and provenance. Current telemetry does not yet measure long-term user outcomes. Do not infer approvals from a conversation or claim causal ROI or salary outcomes from the prototype.

The Navigator routes explicitly refuse non-local environments in this reference version. Removing that deployment block requires a reviewed code change after source, privacy and policy approval; changing an environment token alone does not approve the product.
