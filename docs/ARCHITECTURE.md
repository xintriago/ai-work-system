# Bot Factory Architecture

## Ownership boundaries

### PIX — control plane
Owns deterministic policy, approval matrix, identity, risk, shared memory, budgets, portfolio registry, and audit expectations.

### OpenClaw — runtime
Owns isolated agent sessions, channel bindings, MCP/plugin exposure, workspace access, and sandbox execution.

### Bot Factory — execution layer
Owns job intake, candidate scoring, gate evaluation, task decomposition, bounded delegation, evidence capture, and handoff back to PIX.

## Pipeline

1. **SCOUT** proposes opportunities with evidence.
2. **SCOPE** rejects jobs that cannot fit the configured work-cycle/complexity cap.
3. **DUPE** rejects high-overlap ideas before build spend.
4. **BUILDER** works only inside its assigned repository/workspace.
5. **CRASH** verifies the previous production state and the current candidate's tests.
6. **RISK** vetoes high-risk work; medium risk escalates.
7. **MONEY** enforces hard budget floors; no silent top-ups.
8. **SHIP** can prepare a release but cannot merge/deploy without owner approval.
9. **LEARN** records outcome, cost, defects, and reusable lessons.

## Non-negotiable invariants

- LLMs may recommend; deterministic gates decide whether execution is allowed.
- An unhealthy last deploy blocks new feature shipment.
- High-risk work is rejected automatically.
- Medium-risk work requires owner review.
- Budget floors are fail-closed.
- Merge/deploy, payments, secrets, destructive actions, and external messages require exact approval.
- `ship` does not inherit builder write access to production.
- Audit records are append-oriented and must contain gate reasons.

## Model routing

Bot Factory does not hard-code a provider. PIX/OpenClaw should route economy work first and escalate only when needed. Current preferred direction:

`NVIDIA NIM -> OpenRouter :free -> local Ollama -> paid escalation`

Routing must never weaken tool permissions or approval rules.
