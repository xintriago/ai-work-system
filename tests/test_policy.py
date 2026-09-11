import unittest

from bot_factory.models import ActionClass, BuildCandidate, Decision, RiskLevel, RuntimeState
from bot_factory.policy import PolicyEngine


class PolicyEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = PolicyEngine()
        self.state = RuntimeState(last_deploy_healthy=True, available_balance_usd=100.0)

    def candidate(self, **overrides):
        data = dict(
            name="small-tool",
            estimated_hours=4,
            complexity_points=20,
            duplicate_score=0.2,
            risk=RiskLevel.LOW,
            estimated_cost_usd=5,
            action=ActionClass.BUILD,
        )
        data.update(overrides)
        return BuildCandidate(**data)

    def test_low_risk_bounded_build_passes(self):
        result = self.engine.evaluate(self.candidate(), self.state)
        self.assertEqual(result.final_decision, Decision.PASS)

    def test_unhealthy_last_deploy_blocks_new_work(self):
        state = RuntimeState(last_deploy_healthy=False, available_balance_usd=100)
        result = self.engine.evaluate(self.candidate(), state)
        self.assertEqual(result.final_decision, Decision.BLOCK)

    def test_high_duplicate_rejected(self):
        result = self.engine.evaluate(self.candidate(duplicate_score=0.95), self.state)
        self.assertEqual(result.final_decision, Decision.REJECT)

    def test_negative_probability_weighted_value_rejected(self):
        result = self.engine.evaluate(
            self.candidate(
                expected_benefit_usd=10,
                confidence=0.5,
                estimated_cost_usd=6,
                execution_overhead_usd=1,
            ),
            self.state,
        )
        self.assertEqual(result.final_decision, Decision.REJECT)

    def test_positive_probability_weighted_value_passes(self):
        result = self.engine.evaluate(
            self.candidate(
                expected_benefit_usd=40,
                confidence=0.75,
                estimated_cost_usd=6,
                execution_overhead_usd=2,
            ),
            self.state,
        )
        self.assertEqual(result.final_decision, Decision.PASS)

    def test_high_risk_vetoed(self):
        result = self.engine.evaluate(self.candidate(risk=RiskLevel.HIGH), self.state)
        self.assertEqual(result.final_decision, Decision.REJECT)

    def test_medium_risk_escalates(self):
        result = self.engine.evaluate(self.candidate(risk=RiskLevel.MEDIUM), self.state)
        self.assertEqual(result.final_decision, Decision.NEEDS_APPROVAL)

    def test_budget_floor_fails_closed(self):
        result = self.engine.evaluate(self.candidate(estimated_cost_usd=95), self.state)
        self.assertEqual(result.final_decision, Decision.BLOCK)

    def test_deploy_requires_owner_approval(self):
        result = self.engine.evaluate(self.candidate(action=ActionClass.DEPLOY), self.state)
        self.assertEqual(result.final_decision, Decision.NEEDS_APPROVAL)

    def test_exact_approval_unblocks_deploy_gate(self):
        state = RuntimeState(last_deploy_healthy=True, available_balance_usd=100, owner_approved=True)
        result = self.engine.evaluate(self.candidate(action=ActionClass.DEPLOY), state)
        self.assertEqual(result.final_decision, Decision.PASS)


if __name__ == "__main__":
    unittest.main()
