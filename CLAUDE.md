# Bot Factory Developer Contract

## Mission
Build the execution layer for Xavier's autonomous agent workforce without creating a second control plane.

## Read first
1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/STATE.md`
4. PIX governance files before changing approval behavior

## Authority
- PIX is authoritative for governance and approvals.
- OpenClaw is authoritative for agent runtime/sandbox behavior.
- This repo implements bounded jobs, deterministic gates, adapters, evidence, and learning loops.

## Hard rules
- Never make an LLM able to bypass deterministic gates.
- Never silently top up or cross the configured budget floor.
- Never merge/deploy/send/pay/delete/rotate secrets without exact owner approval.
- Builder gets only assigned-repo write access.
- Risk/reviewer agents are read-only.
- Ship may prepare release artifacts but remains read-only until the approval gate is satisfied.
- Preserve an auditable reason for every reject/block/approval decision.

## Autonomous loop
1. Read `docs/STATE.md`.
2. Pick the highest-value unfinished item that does not require owner approval.
3. Implement narrowly.
4. Test.
5. Fix failures.
6. Update state.
7. Commit/push only when the user's request clearly authorizes publishing repo changes.
8. Never merge/deploy without separate explicit approval.
