# Bot Factory State

LAST UPDATED: 2026-09-11
STATUS: v0.1 review branch implemented and locally validated

COMPLETED:
- Clarified PIX / OpenClaw / Bot Factory ownership boundaries.
- Added deterministic SCOPE, DUPE, VALUE, CRASH, RISK, MONEY, and APPROVAL gates.
- Added bounded candidate prioritization.
- Added confidence-weighted net-value calculation for measurable opportunities.
- Added bounded resource envelopes for autonomous time/cost allocation.
- Added append-only JSONL audit events for repeated stage checks.
- Added agent manifest and OpenClaw sandbox reference config.
- Added external-pattern adoption notes for the 0xCristal and Daniro examples.
- Added CI workflow and 14 locally validated unit tests.

NEXT:
1. Add OpenClaw job adapter and stage-by-stage re-evaluation hooks.
2. Add Telegram approval envelope compatible with PIX approval semantics.
3. Add GitHub PR/check evidence collector.
4. Add model-router adapter with usage/cost accounting.
5. Add CLOSE/LEARN post-run evaluator and compact project-memory update.

BLOCKED / OWNER-GATED:
- Production deploys and merges.
- External messages.
- Paid API/subscription actions.
- Secret and permission changes.
