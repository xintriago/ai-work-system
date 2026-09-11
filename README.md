# AI Work System — Bot Factory

Bot Factory is the execution layer for Xavier's agent workforce. It is **not** a second AI operating system.

- **PIX** owns governance, approvals, risk policy, budgets, shared memory, and audit rules.
- **OpenClaw** owns agent sessions, channel routing, sandboxes, tools, and runtime isolation.
- **Bot Factory** turns approved goals into bounded agent jobs and enforces deterministic gates before work can advance.

## v0.1

This bootstrap implements the first rule-based production pipeline inspired by the useful patterns in the referenced Grok Bot/Ship Studio example:

`SCOUT -> SCOPE -> DUPE -> BUILD -> CRASH -> RISK -> MONEY -> SHIP -> LEARN`

The key difference is that model judgment never overrides deterministic owner gates. Production deploys, merges, payments, secrets, destructive actions, and external communications remain approval-gated by PIX.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Design goals

1. Fail closed on unhealthy production state.
2. Prefer small jobs that can complete in one bounded work cycle.
3. Reject likely duplicates before spending build tokens.
4. Veto only high-risk jobs automatically; medium risk is escalated.
5. Enforce budget floors and prohibit silent top-ups.
6. Keep deploy/merge permission separate from build permission.
7. Produce an auditable decision trail for every candidate.
