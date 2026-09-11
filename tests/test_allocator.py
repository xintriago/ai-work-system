import unittest

from bot_factory.allocator import ResourceAllocator
from bot_factory.models import BuildCandidate, RiskLevel, RuntimeState


class ResourceAllocatorTests(unittest.TestCase):
    def test_caps_cost_to_small_fraction_of_available_budget(self):
        candidate = BuildCandidate("task", 4, 10, 0.1, RiskLevel.LOW, estimated_cost_usd=20)
        state = RuntimeState(available_balance_usd=100)
        envelope = ResourceAllocator().allocate(candidate, state)
        self.assertEqual(envelope.max_cost_usd, 9.0)
        self.assertFalse(envelope.estimate_fits)

    def test_small_estimate_gets_limited_headroom(self):
        candidate = BuildCandidate("task", 4, 10, 0.1, RiskLevel.LOW, estimated_cost_usd=5)
        state = RuntimeState(available_balance_usd=100)
        envelope = ResourceAllocator().allocate(candidate, state)
        self.assertEqual(envelope.max_cost_usd, 6.25)
        self.assertTrue(envelope.estimate_fits)


if __name__ == "__main__":
    unittest.main()
