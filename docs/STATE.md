# Bot Factory State

LAST UPDATED: 2026-10-31
STATUS: capability-promotion gate implemented and locally validated; external activation remains owner-gated

COMPLETED:
- Clarified PIX / OpenClaw / Bot Factory ownership boundaries.
- Added deterministic SCOPE, DUPE, VALUE, CRASH, RISK, MONEY, and APPROVAL gates.
- Added bounded candidate prioritization.
- Added confidence-weighted net-value calculation for measurable opportunities.
- Added bounded resource envelopes for autonomous time/cost allocation.
- Added append-only JSONL audit events for repeated stage checks.
- Added stage-by-stage run controller that re-evaluates policy before later execution boundaries.
- Added exact-action approval envelopes with request fingerprints so stale approvals cannot authorize changed operations.
- Hardened OpenClaw sandbox reference: session isolation, read-only root, no shell egress, dropped Linux capabilities.
- Added external-pattern adoption notes for the 0xCristal and Daniro examples.
- Added CI workflow and 20 locally validated unit tests.
- Added deterministic repeated-process promotion: SOP, duplicate check, tested-skill evidence and optional-automation approval boundary.
- Added change-control completeness gate with independent review for medium/high risk.
- Added default-deny humanizer scope for QA, compliance, contracts, code and technical results.
- Added 16 focused tests for the new gates; full local suite now contains 36 tests.

NEXT:
1. Add OpenClaw job/session adapter using Gateway-managed sandboxed workers.
2. Add Telegram transport for the approval envelope.
3. Add GitHub PR/check evidence collector.
4. Add model-router adapter with usage/cost accounting.
5. Add CLOSE/LEARN post-run evaluator and compact project-memory update.
6. Integrate these advisory results with PIX only after Completion Mode allows runtime feature work; do not add a second memory or control plane.

BLOCKED / OWNER-GATED:
- Production deploys and merges.
- External messages.
- Paid API/subscription actions.
- Secret and permission changes.

