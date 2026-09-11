import unittest

from bot_factory.approval import ApprovalGuard, ApprovalOutcome, ApprovalRequest


class ApprovalTests(unittest.TestCase):
    def request(self, **overrides):
        data = dict(
            request_id="approve-1",
            action="deploy",
            target="bot-factory",
            environment="production",
            external_effect="publish release",
            max_cost_usd=0.0,
            data_exposed="none",
            rollback="revert deployment",
            evidence="tests passing",
        )
        data.update(overrides)
        return ApprovalRequest(**data)

    def test_approved_token_validates_exact_request(self):
        request = self.request()
        token = ApprovalGuard.issue(request, ApprovalOutcome.APPROVED)
        self.assertTrue(ApprovalGuard.validates(request, token))

    def test_changed_target_invalidates_previous_approval(self):
        original = self.request()
        token = ApprovalGuard.issue(original, ApprovalOutcome.APPROVED)
        changed = self.request(target="different-repo")
        self.assertFalse(ApprovalGuard.validates(changed, token))

    def test_changed_cost_invalidates_previous_approval(self):
        original = self.request()
        token = ApprovalGuard.issue(original, ApprovalOutcome.APPROVED)
        changed = self.request(max_cost_usd=25.0)
        self.assertFalse(ApprovalGuard.validates(changed, token))

    def test_rejected_token_never_authorizes(self):
        request = self.request()
        token = ApprovalGuard.issue(request, ApprovalOutcome.REJECTED)
        self.assertFalse(ApprovalGuard.validates(request, token))


if __name__ == "__main__":
    unittest.main()
