import json
import tempfile
import unittest
from pathlib import Path

from bot_factory.audit import JsonlAuditWriter
from bot_factory.models import BuildCandidate, RiskLevel, RuntimeState
from bot_factory.policy import PolicyEngine


class AuditTests(unittest.TestCase):
    def test_evaluation_is_appended_as_jsonl(self):
        candidate = BuildCandidate("audit-task", 2, 10, 0.1, RiskLevel.LOW, estimated_cost_usd=1)
        evaluation = PolicyEngine().evaluate(candidate, RuntimeState(available_balance_usd=100))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "audit.jsonl"
            writer = JsonlAuditWriter(path)
            writer.append_evaluation("run-1", "preflight", evaluation)
            writer.append_evaluation("run-1", "pre-ship", evaluation)

            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            first = json.loads(lines[0])
            second = json.loads(lines[1])
            self.assertEqual(first["event_type"], "policy_evaluation")
            self.assertEqual(first["stage"], "preflight")
            self.assertEqual(second["stage"], "pre-ship")
            self.assertEqual(first["payload"]["candidate"], "audit-task")


if __name__ == "__main__":
    unittest.main()
