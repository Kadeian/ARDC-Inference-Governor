# NVIT workstreams

Architecture lead owns scope, contracts, reviews, budget and sponsor communication. Assign named students after availability and access are known. Students work in local demos and restricted staging with least privilege; production and policy approval remain with designated staff.

| Workstream | Deliverables | Acceptance / reviewer |
|---|---|---|
| API + agent integration | Adapter, provider usage accounting, auth integration, error handling | Platform + agent owner review; no hidden calls; cancellation and quota tests |
| Governance + evaluation | ARDC decision table integration, adversarial corpus, evaluation report | Policy owner signs rules; independent reviewer checks expected outcomes |
| Platform + reliability | Docker, Terraform, release gates, dashboards, rollback rehearsal | Architecture lead reviews plan and costs; another student executes documented recovery |

Use weekly planning/demo, two short unblock sessions, and a decision log. Each issue includes owner, acceptance criteria, dependency, risk, reviewer and evidence link. Require one reviewer outside the author's workstream. Rotate demos and incident rehearsal roles. Track completed reviews and architectural decisions rather than only ticket count.

Starter backlog: C4L-001 agent inventory; 002 policy decision table; 003 adapter contract tests; 004 quality corpus; 005 tenant auth; 006 distributed budgets; 007 staging network/secret plan; 008 telemetry wiring; 009 rollback drill; 010 website backend integration. Dependencies: 001/002 before 003/004, 005/006/007/008 before 009, all production gates before 010 launch.

Definition of done: reproducible check, security/privacy consideration, docs updated, independent review and demo evidence. Escalate blocked policy questions to the policy owner; never invent a rule to close a ticket. Record decisions as context, options, decision, owner, consequences and revisit date. Keep a weekly leadership log of delegated scope, review feedback, resolved tradeoffs and measured outcomes.
