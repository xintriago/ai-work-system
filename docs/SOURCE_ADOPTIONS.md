# External Pattern Adoptions

This file records ideas borrowed from public examples without importing proprietary code or treating promotional claims as verified performance.

## 2026-09-11 — 0xCristal Ship Studio thread

Source: https://x.com/0xCristal/status/2093438799602991285

Adopted patterns:
- Separate scope, duplicate, failure, risk, budget, ship, and learning responsibilities.
- Keep release authority separate from build authority.
- Stop new feature work when the previous production state is unhealthy.
- Use a repeatable agent pipeline with explicit veto points.

Adaptation:
- Implemented as deterministic policy gates under PIX governance rather than model-only prompts.
- Production merge/deploy remains exact-owner-approval gated.

## 2026-09-11 — Daniro multi-agent trading-desk post

Source: https://x.com/Dan1ro0/status/2096656286553153709

Public search mirrors around the referenced post describe a specialist chain such as detection -> probability update -> edge validation -> sizing -> execution -> closing/cleanup. Reported trading returns are not treated as verified evidence.

Adopted patterns:
- Sequential specialist handoffs instead of one all-purpose agent.
- Recalculate conditions before later execution stages.
- Validate expected benefit after cost/overhead before spending resources when value is measurable.
- Give executors bounded resource envelopes rather than open-ended budgets.
- Treat closing/cleanup and residual-state verification as a first-class stage.

Adaptation for Bot Factory:
- `SCOUT -> ESTIMATE -> VALUE -> ALLOCATE -> BUILD -> VERIFY -> RISK -> SHIP -> CLOSE -> LEARN`
- No trading strategy or live-trading behavior is imported.
