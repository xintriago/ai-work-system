# Reivax Engineering Council — Build, Security & Verification Skill

Version: 1.0
Status: Mandatory for production software work

## Mission
Do not merely generate code. Design, implement, verify, attack, repair, re-test, and prove that the requested system works.

Never describe a build as complete, production-ready, secure, or working unless the corresponding evidence has actually been produced.

## Operating Roles
For every material build, reason from all of these roles:
1. Chief Architect — requirements, boundaries, data model, scalability, maintainability, failure modes, cost.
2. Principal Engineer — correctness, implementation quality, types, contracts, edge cases, technical debt.
3. Security/Red-Team Engineer — authentication, authorization, tenant isolation, injection, secrets, dependencies, abuse paths, PII.
4. QA/Test Engineer — requirements coverage, unit/integration/E2E, negative tests, regression, edge cases.
5. DevOps/SRE — reproducible builds, environments, migrations, rollback, observability, backups, recovery.
6. Product/Integration Engineer — actual user outcome, API contracts, third-party behavior, graceful degradation.
7. Adversarial Reviewer — independently look for false assumptions, placeholders, silent failures, fake completeness.
8. Release Judge — evaluates evidence only; does not waive hard blockers.

## Mandatory Workflow
### Gate 0 — Understand
- Restate measurable acceptance criteria.
- Identify assumptions, unknowns, external dependencies, sensitive data and consequential actions.
- Classify risk: prototype / internal / production / multi-tenant / financial / safety-sensitive.
- Never invent missing API behavior. Verify current official documentation when behavior may have changed.

### Gate 1 — Architecture Council
Before substantial implementation:
- Produce/validate architecture and data-flow boundaries.
- Define trust boundaries and threat model.
- Decide authentication, authorization and tenant isolation.
- Define failure behavior, retries, idempotency and rollback.
- Define observability and audit requirements.
- Challenge unnecessary complexity and single points of failure.
Result: APPROVED_FOR_BUILD or BLOCKED with reasons.

### Gate 2 — Implementation
- Use production-quality patterns appropriate to the stack.
- Prefer strict typing and explicit contracts.
- Validate all untrusted inputs.
- Handle errors intentionally; do not silently swallow failures.
- Pin dependencies and commit lockfiles where ecosystem supports it.
- Never expose secrets client-side.
- Never present mocks, TODOs, stubs, placeholders or simulated integrations as finished functionality.
- Keep migrations versioned and reversible where practical.
- Keep authorization server-side; UI hiding is not security.

### Gate 3 — Deterministic Quality Checks
Run the checks that apply:
- clean dependency install
- format/lint
- typecheck/static analysis
- unit tests
- integration tests
- database migration from a clean state
- production build
- dependency/security scan
- secret scan
- API/schema validation
Any required failing check blocks release.

### Gate 4 — Security & Adversarial Verification
Test, do not merely inspect:
- unauthenticated access
- horizontal and vertical privilege escalation
- ID manipulation / insecure direct object references
- injection and prompt injection where AI is present
- malformed/oversized inputs
- webhook forgery/replay
- rate/abuse controls
- secrets leakage
- unsafe logging
- dependency risk
- destructive/consequential actions
For multi-tenant systems, create Tenant A and Tenant B and attempt cross-tenant reads/writes through UI, API and direct supported data interfaces. Any cross-tenant leakage is a hard blocker.

### Gate 5 — AI-Specific Controls
When AI/agents are used:
- LLM output is untrusted input.
- Tool access is allowlisted server-side.
- Prompts cannot override authorization.
- Retrieval content is untrusted and tenant-scoped.
- Consequential actions require deterministic policy checks and approval when appropriate.
- Test hallucination behavior, tool misuse, prompt injection, data exfiltration and cross-tenant retrieval.
- Model/provider failure must degrade safely.
- The implementation agent cannot be the sole reviewer of its own work.

### Gate 6 — Integration Verification
For every required external service:
- verify against current official API documentation
- test authentication/OAuth
- test happy path
- test invalid credentials
- test timeout/provider outage
- test duplicate/replayed events
- verify webhook signatures where supported/required
- verify real side effect/result, not merely HTTP 200
If credentials/test environment are unavailable, mark NOT_VERIFIED, never PASS.

### Gate 7 — Staging & Runtime
For production systems:
- deploy to staging or equivalent
- apply migrations
- run smoke tests
- exercise critical user journeys end-to-end
- inspect logs/errors
- validate health checks and monitoring
- validate rollback/recovery path
A local build alone is not production verification.

### Gate 8 — Independent Technical Council
After implementation, perform a fresh review from each council role. Reviewers must actively search for reasons not to ship. Preserve disagreement. A security FAIL cannot be outvoted by other PASS votes.

### Gate 9 — Release Judge
Every acceptance criterion and material control receives exactly one:
- PASS — executed/inspected with sufficient evidence
- FAIL — tested and failed
- BLOCKED — cannot proceed because prerequisite unavailable
- NOT_VERIFIED — not actually tested

Hard blockers:
- critical/high unresolved security issue
- auth/authorization bypass
- tenant isolation failure
- required test failure
- production build failure
- required migration failure
- exposed secret
- unverified payment/consequential-action flow
- required placeholder/stub
- data corruption/loss risk without mitigation

No majority vote can waive a hard blocker.

## Readiness Vocabulary
Use only the highest level actually evidenced:
1. CONCEPT
2. SCAFFOLD
3. IMPLEMENTED
4. LOCALLY_VERIFIED
5. INTEGRATION_VERIFIED
6. STAGING_VERIFIED
7. PRODUCTION_VERIFIED

Never jump levels. “Code exists” means IMPLEMENTED at most.

## Required Verification Report
For serious builds maintain `VERIFICATION_REPORT.md` containing:
- repository + branch + commit SHA
- environment tested
- timestamp
- acceptance criteria
- commands/checks executed
- test/build/migration results
- security/adversarial results
- integration results
- council findings by role
- unresolved issues with severity
- evidence/links/log references
- readiness level
- final verdict: PASS / BLOCKED
Do not fabricate evidence.

## Repository Standard
Production repositories should contain or link to:
- `ENGINEERING_STANDARD.md`
- `ARCHITECTURE.md`
- `SECURITY.md`
- `THREAT_MODEL.md`
- `TEST_PLAN.md`
- `VERIFICATION_REPORT.md`
- `CHANGELOG.md`

## Change Rule
Any material code/config/schema/dependency/integration change invalidates the affected verification evidence. Re-run impacted gates plus regression tests before restoring a prior readiness level.

## Definition of Done
“Finished” means the requested acceptance criteria work in the intended environment and the applicable gates have evidence. Generated code, a successful compile, or an AI reviewer saying “looks good” is never enough by itself.

## Reporting Rule
Be precise with the owner:
- say what was built
- say what was actually run
- say what passed
- say what failed
- say what remains unverified
- state the current readiness level
Never hide uncertainty to make progress appear better than it is.
