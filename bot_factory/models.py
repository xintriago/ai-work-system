from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Decision(StrEnum):
    PASS = "pass"
    REJECT = "reject"
    BLOCK = "block"
    NEEDS_APPROVAL = "needs_approval"


class ActionClass(StrEnum):
    RESEARCH = "research"
    BUILD = "build"
    MERGE = "merge"
    DEPLOY = "deploy"
    EXTERNAL_MESSAGE = "external_message"
    PAYMENT = "payment"
    SECRET_CHANGE = "secret_change"
    DESTRUCTIVE = "destructive"


@dataclass(frozen=True, slots=True)
class BuildCandidate:
    name: str
    estimated_hours: float
    complexity_points: int
    duplicate_score: float
    risk: RiskLevel
    estimated_cost_usd: float = 0.0
    action: ActionClass = ActionClass.BUILD
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RuntimeState:
    last_deploy_healthy: bool = True
    available_balance_usd: float = 0.0
    owner_approved: bool = False


@dataclass(frozen=True, slots=True)
class GateResult:
    gate: str
    decision: Decision
    reason: str


@dataclass(frozen=True, slots=True)
class Evaluation:
    candidate: BuildCandidate
    final_decision: Decision
    gates: tuple[GateResult, ...]

    @property
    def allowed_to_build(self) -> bool:
        return self.final_decision in {Decision.PASS, Decision.NEEDS_APPROVAL}
