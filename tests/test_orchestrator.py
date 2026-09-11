import unittest

from bot_factory.models import BuildCandidate, Decision, RiskLevel, RuntimeState
from bot_factory.orchestrator import BotFactoryOrchestrator


class OrchestratorTests(unittest.TestCase):
    def test_pass_candidates_rank_before_rejected_candidates(self):
        state = RuntimeState(last_deploy_healthy=True, available_balance_usd=100)
        candidates = [
            BuildCandidate("duplicate", 2, 10, 0.95, RiskLevel.LOW, 1),
            BuildCandidate("good", 4, 20, 0.10, RiskLevel.LOW, 2),
        ]
        ranked = BotFactoryOrchestrator().prioritize(candidates, state)
        self.assertEqual(ranked[0].evaluation.candidate.name, "good")
        self.assertEqual(ranked[0].evaluation.final_decision, Decision.PASS)
        self.assertEqual(ranked[1].evaluation.final_decision, Decision.REJECT)


if __name__ == "__main__":
    unittest.main()
