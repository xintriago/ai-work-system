from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .models import Decision, RiskLevel


class ProcessStage(StrEnum):
    OBSERVED = "observed"
    SOP_REQUIRED = "sop_required"
    REUSE_EXISTING = "reuse_existing"
    SKILL_CANDIDATE = "skill_candidate"
    TESTED_SKILL = "tested_skill"
    OPTIONAL_AUTOMATION = "optional_automation"


@dataclass(frozen=True, slots=True)
class SkillTestEvidence:
    valid_case_id: str
    failure_or_abstention_case_id: str
    regression_case_id: str

    @property
    def complete(self) -> bool:
        values = tuple(
            value.strip()
            for value in (
                self.valid_case_id,
                self.failure_or_abstention_case_id,
                self.regression_case_id,
            )
        )
        return all(values) and len(set(values)) == len(values)


@dataclass(frozen=True, slots=True)
class ProcessEvidence:
    """Evidence used to promote a repeated process without creating duplicates."""

    process_id: str
    occurrence_evidence: tuple[str, ...] = ()
    duplicate_check_id: str | None = None
    sop_id: str | None = None
    existing_capability_id: str | None = None
    test_evidence: SkillTestEvidence | None = None
    independent_review_id: str | None = None
    automation_requested: bool = False


@dataclass(frozen=True, slots=True)
class ProcessPromotionResult:
    stage: ProcessStage
    decision: Decision
    reasons: tuple[str, ...]
    activation_allowed: bool = False


class ProcessPromotionGate:
    """Implements Repeated Process -> SOP -> tested skill -> gated automation.

    The gate classifies readiness only. It never installs a skill, schedules a
    worker, or bypasses PIX's exact-action approval controls.
    """

    def __init__(self, min_repetitions: int = 3) -> None:
        if min_repetitions < 2:
            raise ValueError("min_repetitions must be at least 2")
        self.min_repetitions = min_repetitions

    def evaluate(self, evidence: ProcessEvidence) -> ProcessPromotionResult:
        if not evidence.process_id.strip():
            return ProcessPromotionResult(
                ProcessStage.OBSERVED,
                Decision.BLOCK,
                ("process_id is required",),
            )

        unique_occurrences = tuple(dict.fromkeys(evidence.occurrence_evidence))
        if len(unique_occurrences) < self.min_repetitions:
            return ProcessPromotionResult(
                ProcessStage.OBSERVED,
                Decision.BLOCK,
                (
                    f"need {self.min_repetitions} distinct occurrence records; "
                    f"found {len(unique_occurrences)}",
                ),
            )

        if not evidence.duplicate_check_id:
            return ProcessPromotionResult(
                ProcessStage.REUSE_EXISTING,
                Decision.BLOCK,
                ("record a duplicate search before creating or promoting a skill candidate",),
            )

        if evidence.existing_capability_id:
            return ProcessPromotionResult(
                ProcessStage.REUSE_EXISTING,
                Decision.REJECT,
                (f"reuse or extend existing capability {evidence.existing_capability_id}",),
            )

        if not evidence.sop_id:
            return ProcessPromotionResult(
                ProcessStage.SOP_REQUIRED,
                Decision.BLOCK,
                ("document the current process, exceptions, owner, evidence, and capacity before promotion",),
            )

        if evidence.test_evidence is None:
            return ProcessPromotionResult(
                ProcessStage.SKILL_CANDIDATE,
                Decision.NEEDS_APPROVAL,
                ("candidate is documented but has no executed scenario evidence",),
            )

        if not evidence.test_evidence.complete:
            return ProcessPromotionResult(
                ProcessStage.SKILL_CANDIDATE,
                Decision.BLOCK,
                ("tested-skill promotion requires distinct valid, failure/abstention, and regression evidence",),
            )

        if not evidence.independent_review_id:
            return ProcessPromotionResult(
                ProcessStage.SKILL_CANDIDATE,
                Decision.BLOCK,
                ("independent review evidence is required before tested-skill promotion",),
            )

        if evidence.automation_requested:
            return ProcessPromotionResult(
                ProcessStage.OPTIONAL_AUTOMATION,
                Decision.NEEDS_APPROVAL,
                (
                    "skill is tested; automation remains optional and must pass PIX's existing "
                    "exact-action approval, risk, budget, and runtime gates",
                ),
            )

        return ProcessPromotionResult(
            ProcessStage.TESTED_SKILL,
            Decision.PASS,
            ("documented skill has executed test and independent review evidence",),
        )


@dataclass(frozen=True, slots=True)
class ChangeControlResult:
    decision: Decision
    missing: tuple[str, ...]
    execution_authorized: bool = False


@dataclass(frozen=True, slots=True)
class ChangeControlRequest:
    title: str
    risk: RiskLevel
    impact_analysis: str = ""
    test_plan: str = ""
    rollback_plan: str = ""
    verification_plan: str = ""
    independent_review_id: str | None = None

    def evaluate(self) -> ChangeControlResult:
        required = {
            "title": self.title,
            "impact_analysis": self.impact_analysis,
            "test_plan": self.test_plan,
            "rollback_plan": self.rollback_plan,
            "verification_plan": self.verification_plan,
        }
        missing = [name for name, value in required.items() if not value.strip()]
        if self.risk in {RiskLevel.MEDIUM, RiskLevel.HIGH} and not self.independent_review_id:
            missing.append("independent_review_id")

        if missing:
            decision = Decision.BLOCK
        elif self.risk is RiskLevel.HIGH:
            decision = Decision.REJECT
        elif self.risk is RiskLevel.MEDIUM:
            decision = Decision.NEEDS_APPROVAL
        else:
            decision = Decision.PASS

        return ChangeControlResult(decision=decision, missing=tuple(missing))


class ContentKind(StrEnum):
    MARKETING = "marketing"
    SALES = "sales"
    ZEN_PAWS = "zen_paws"
    EXTERNAL_COMMUNICATION = "external_communication"
    QA = "qa"
    COMPLIANCE = "compliance"
    CONTRACT = "contract"
    CODE = "code"
    TECHNICAL_RESULT = "technical_result"


@dataclass(frozen=True, slots=True)
class HumanizerResult:
    allowed: bool
    reason: str


class HumanizerPolicy:
    """Default-deny scope for tone-only external copy editing."""

    _ALLOWED = frozenset(
        {
            ContentKind.MARKETING,
            ContentKind.SALES,
            ContentKind.ZEN_PAWS,
            ContentKind.EXTERNAL_COMMUNICATION,
        }
    )

    def evaluate(
        self,
        content_kind: ContentKind,
        *,
        includes_controlled_content: bool = False,
    ) -> HumanizerResult:
        if includes_controlled_content:
            return HumanizerResult(
                False,
                "mixed or controlled content must be separated before any tone rewrite",
            )
        if content_kind in self._ALLOWED:
            return HumanizerResult(
                True,
                "tone-only rewrite allowed; claims, numbers, approvals, and source evidence must remain unchanged",
            )
        return HumanizerResult(
            False,
            "humanizer is prohibited for QA, compliance, contracts, code, and technical results",
        )
