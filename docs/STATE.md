# Bot Factory State

LAST UPDATED: 2026-09-11
STATUS: v0.1 bootstrap implemented and testable

COMPLETED:
- Clarified PIX / OpenClaw / Bot Factory ownership boundaries.
- Added deterministic SCOPE, DUPE, CRASH, RISK, MONEY, and APPROVAL gates.
- Added bounded candidate prioritization.
- Added agent manifest and OpenClaw sandbox reference config.
- Added unit tests for fail-closed behavior.

NEXT:
1. Add append-only audit event schema + JSONL writer.
2. Add OpenClaw job adapter and Telegram approval envelope.
3. Add GitHub PR/check evidence collector.
4. Add model-router adapter with usage/cost accounting.
5. Add LEARN post-run evaluator and compact project-memory update.

BLOCKED / OWNER-GATED:
- Production deploys and merges.
- External messages.
- Paid API/subscription actions.
- Secret and permission changes.
