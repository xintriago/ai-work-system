import unittest

from bot_factory.capability_gates import (
    ChangeControlRequest,
    ContentKind,
    HumanizerPolicy,
    ProcessEvidence,
    ProcessPromotionGate,
    ProcessStage,
    SkillTestEvidence,
)
from bot_factory.models import Decision, RiskLevel


class ProcessPromotionGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = ProcessPromotionGate(min_repetitions=3)

    def test_repeated_process_needs_sop_before_skill_candidate(self):
        result = self.gate.evaluate(
            ProcessEvidence(
                process_id="invoice-reconciliation",
                occurrence_evidence=("run-1", "run-2", "run-3"),
                duplicate_check_id="dupe-check-1",
            )
        )

        self.assertEqual(result.stage, ProcessStage.SOP_REQUIRED)
        self.assertEqual(result.decision, Decision.BLOCK)
        self.assertFalse(result.activation_allowed)

    def test_existing_capability_is_reused_instead_of_duplicated(self):
        result = self.gate.evaluate(
            ProcessEvidence(
                process_id="vendor-review",
                occurrence_evidence=("run-1", "run-2", "run-3"),
                duplicate_check_id="dupe-check-1",
                existing_capability_id="pix-negocio-operaciones",
            )
        )

        self.assertEqual(result.stage, ProcessStage.REUSE_EXISTING)
        self.assertEqual(result.decision, Decision.REJECT)
        self.assertIn("pix-negocio-operaciones", result.reasons[0])

    def test_sop_can_become_a_skill_candidate_but_not_activate(self):
        result = self.gate.evaluate(
            ProcessEvidence(
                process_id="capacity-review",
                occurrence_evidence=("run-1", "run-2", "run-3"),
                duplicate_check_id="dupe-check-1",
                sop_id="sop-capacity-review-v1",
            )
        )

        self.assertEqual(result.stage, ProcessStage.SKILL_CANDIDATE)
        self.assertEqual(result.decision, Decision.NEEDS_APPROVAL)
        self.assertFalse(result.activation_allowed)

    def test_tested_and_independently_reviewed_candidate_is_tested_skill(self):
        result = self.gate.evaluate(
            ProcessEvidence(
                process_id="capacity-review",
                occurrence_evidence=("run-1", "run-2", "run-3"),
                duplicate_check_id="dupe-check-1",
                sop_id="sop-capacity-review-v1",
                test_evidence=SkillTestEvidence(
                    valid_case_id="valid-case",
                    failure_or_abstention_case_id="failure-case",
                    regression_case_id="regression-case",
                ),
                independent_review_id="review-42",
            )
        )

        self.assertEqual(result.stage, ProcessStage.TESTED_SKILL)
        self.assertEqual(result.decision, Decision.PASS)
        self.assertFalse(result.activation_allowed)

    def test_duplicate_check_is_required_before_skill_candidate(self):
        result = self.gate.evaluate(
            ProcessEvidence(
                process_id="capacity-review",
                occurrence_evidence=("run-1", "run-2", "run-3"),
                sop_id="sop-capacity-review-v1",
            )
        )

        self.assertEqual(result.stage, ProcessStage.REUSE_EXISTING)
        self.assertEqual(result.decision, Decision.BLOCK)

    def test_each_test_category_needs_distinct_evidence(self):
        result = self.gate.evaluate(
            ProcessEvidence(
                process_id="capacity-review",
                occurrence_evidence=("run-1", "run-2", "run-3"),
                duplicate_check_id="dupe-check-1",
                sop_id="sop-capacity-review-v1",
                test_evidence=SkillTestEvidence(
                    valid_case_id="same-case",
                    failure_or_abstention_case_id="same-case",
                    regression_case_id="",
                ),
                independent_review_id="review-42",
            )
        )

        self.assertEqual(result.stage, ProcessStage.SKILL_CANDIDATE)
        self.assertEqual(result.decision, Decision.BLOCK)

    def test_test_evidence_ids_are_compared_after_whitespace_normalization(self):
        evidence = SkillTestEvidence(
            valid_case_id="same-case",
            failure_or_abstention_case_id=" same-case ",
            regression_case_id="regression-case",
        )

        self.assertFalse(evidence.complete)

    def test_optional_automation_always_stays_behind_existing_approval_gate(self):
        result = self.gate.evaluate(
            ProcessEvidence(
                process_id="capacity-review",
                occurrence_evidence=("run-1", "run-2", "run-3"),
                duplicate_check_id="dupe-check-1",
                sop_id="sop-capacity-review-v1",
                test_evidence=SkillTestEvidence(
                    valid_case_id="valid-case",
                    failure_or_abstention_case_id="failure-case",
                    regression_case_id="regression-case",
                ),
                independent_review_id="review-42",
                automation_requested=True,
            )
        )

        self.assertEqual(result.stage, ProcessStage.OPTIONAL_AUTOMATION)
        self.assertEqual(result.decision, Decision.NEEDS_APPROVAL)
        self.assertFalse(result.activation_allowed)


class ChangeControlTests(unittest.TestCase):
    def test_change_requires_impact_test_rollback_and_verification(self):
        result = ChangeControlRequest(title="", risk=RiskLevel.LOW).evaluate()

        self.assertEqual(result.decision, Decision.BLOCK)
        self.assertEqual(
            set(result.missing),
            {"title", "impact_analysis", "test_plan", "rollback_plan", "verification_plan"},
        )

    def test_medium_change_requires_independent_review(self):
        result = ChangeControlRequest(
            title="Change routing",
            risk=RiskLevel.MEDIUM,
            impact_analysis="Affects fallback ordering only.",
            test_plan="Run fallback and outage fixtures.",
            rollback_plan="Revert the routing commit.",
            verification_plan="Confirm primary and fallback evidence.",
        ).evaluate()

        self.assertEqual(result.decision, Decision.BLOCK)
        self.assertEqual(result.missing, ("independent_review_id",))

    def test_complete_low_risk_change_passes_without_authorizing_execution(self):
        result = ChangeControlRequest(
            title="Clarify a briefing template",
            risk=RiskLevel.LOW,
            impact_analysis="Documentation-only.",
            test_plan="Validate required headings.",
            rollback_plan="Restore the previous file revision.",
            verification_plan="Read back the rendered template.",
        ).evaluate()

        self.assertEqual(result.decision, Decision.PASS)
        self.assertFalse(result.execution_authorized)

    def test_reviewed_medium_change_still_needs_owner_approval(self):
        result = ChangeControlRequest(
            title="Change routing",
            risk=RiskLevel.MEDIUM,
            impact_analysis="Affects fallback ordering only.",
            test_plan="Run fallback and outage fixtures.",
            rollback_plan="Revert the routing commit.",
            verification_plan="Confirm primary and fallback evidence.",
            independent_review_id="review-42",
        ).evaluate()

        self.assertEqual(result.decision, Decision.NEEDS_APPROVAL)
        self.assertFalse(result.execution_authorized)

    def test_reviewed_high_risk_change_is_rejected_by_execution_layer(self):
        result = ChangeControlRequest(
            title="Change approval enforcement",
            risk=RiskLevel.HIGH,
            impact_analysis="Touches approval enforcement.",
            test_plan="Run allowed and denied boundary tests.",
            rollback_plan="Revert the policy commit.",
            verification_plan="Confirm deny-by-default behavior.",
            independent_review_id="review-99",
        ).evaluate()

        self.assertEqual(result.decision, Decision.REJECT)
        self.assertFalse(result.execution_authorized)


class HumanizerPolicyTests(unittest.TestCase):
    def test_allows_only_external_marketing_sales_and_zen_paws_copy(self):
        policy = HumanizerPolicy()

        for kind in (
            ContentKind.MARKETING,
            ContentKind.SALES,
            ContentKind.ZEN_PAWS,
            ContentKind.EXTERNAL_COMMUNICATION,
        ):
            with self.subTest(kind=kind):
                self.assertTrue(policy.evaluate(kind).allowed)

    def test_denies_qa_compliance_contracts_code_and_technical_results(self):
        policy = HumanizerPolicy()

        for kind in (
            ContentKind.QA,
            ContentKind.COMPLIANCE,
            ContentKind.CONTRACT,
            ContentKind.CODE,
            ContentKind.TECHNICAL_RESULT,
        ):
            with self.subTest(kind=kind):
                self.assertFalse(policy.evaluate(kind).allowed)

    def test_denies_mixed_external_copy_when_it_contains_controlled_content(self):
        result = HumanizerPolicy().evaluate(
            ContentKind.EXTERNAL_COMMUNICATION,
            includes_controlled_content=True,
        )

        self.assertFalse(result.allowed)


if __name__ == "__main__":
    unittest.main()
