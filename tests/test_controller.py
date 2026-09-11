import tempfile
import unittest
from pathlib import Path

from bot_factory.audit import JsonlAuditWriter
from bot_factory.controller import ExecutionStage, RunController
from bot_factory.models import BuildCandidate, Decision, RiskLevel, RuntimeState


class RunControllerTests(unittest.TestCase):
    def candidate(self):
        return BuildCandidate(
            "controller-task",
            4,
            15,
            0.1,
            RiskLevel.LOW,
            estimated_cost_usd=5,
        )

    def test_rechecks_runtime_state_between_stages(self):
        controller = RunController()
        healthy = controller.check(
            "run-1",
            ExecutionStage.BUILD,
            self.candidate(),
            RuntimeState(last_deploy_healthy=True, available_balance_usd=100),
        )
        unhealthy = controller.check(
            "run-1",
            ExecutionStage.PRE_SHIP,
            self.candidate(),
            RuntimeState(last_deploy_healthy=False, available_balance_usd=100),
        )
        self.assertTrue(healthy.may_continue)
        self.assertEqual(unhealthy.evaluation.final_decision, Decision.BLOCK)
        self.assertFalse(unhealthy.may_continue)

    def test_every_stage_check_can_be_audited(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            controller = RunController(audit=JsonlAuditWriter(path))
            state = RuntimeState(last_deploy_healthy=True, available_balance_usd=100)
            controller.check("run-2", ExecutionStage.PREFLIGHT, self.candidate(), state)
            controller.check("run-2", ExecutionStage.VERIFY, self.candidate(), state)
            self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
