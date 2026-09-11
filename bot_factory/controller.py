from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .allocator import ResourceAllocator, ResourceEnvelope
from .audit import JsonlAuditWriter
from .models import BuildCandidate, Decision, Evaluation, RuntimeState
from .policy import PolicyEngine


class ExecutionStage(StrEnum):
    DISCOVER = "discover"
    PREFLIGHT = "preflight"
    BUILD = "build"
    VERIFY = "verify"
    PRE_SHIP = "pre_ship"
    CLOSE = "close"
    LEARN = "learn"


@dataclass(frozen=True, slots=True)
class StageCheck:
    stage: ExecutionStage
    evaluation: Evaluation
    resource_envelope: ResourceEnvelope

    @property
    def may_continue(self) -> bool:
        return self.evaluation.final_decision is Decision.PASS and self.resource_envelope.estimate_fits

    @property
    def needs_approval(self) -> bool:
        return self.evaluation.final_decision is Decision.NEEDS_APPROVAL


class RunController:
    """Re-checks policy and resource limits at every meaningful execution boundary."""

    def __init__(
        self,
        policy: PolicyEngine | None = None,
        allocator: ResourceAllocator | None = None,
        audit: JsonlAuditWriter | None = None,
    ) -> None:
        self.policy = policy or PolicyEngine()
        self.allocator = allocator or ResourceAllocator()
        self.audit = audit

    def check(
        self,
        run_id: str,
        stage: ExecutionStage,
        candidate: BuildCandidate,
        state: RuntimeState,
    ) -> StageCheck:
        evaluation = self.policy.evaluate(candidate, state)
        envelope = self.allocator.allocate(candidate, state)

        if self.audit is not None:
            self.audit.append_evaluation(run_id, stage.value, evaluation)

        return StageCheck(stage=stage, evaluation=evaluation, resource_envelope=envelope)
