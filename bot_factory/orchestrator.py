from __future__ import annotations

from dataclasses import dataclass

from .models import BuildCandidate, Evaluation, RuntimeState
from .policy import PolicyEngine


@dataclass(slots=True)
class PrioritizedCandidate:
    evaluation: Evaluation
    priority_score: float


class BotFactoryOrchestrator:
    """Ranks candidates only after deterministic policy evaluation."""

    def __init__(self, policy: PolicyEngine | None = None) -> None:
        self.policy = policy or PolicyEngine()

    def prioritize(
        self,
        candidates: list[BuildCandidate],
        state: RuntimeState,
    ) -> list[PrioritizedCandidate]:
        evaluated = [self.policy.evaluate(candidate, state) for candidate in candidates]
        ranked = [
            PrioritizedCandidate(evaluation=item, priority_score=self._score(item.candidate))
            for item in evaluated
        ]
        return sorted(
            ranked,
            key=lambda item: (
                self._decision_rank(item.evaluation.final_decision),
                -item.priority_score,
                item.evaluation.candidate.name.lower(),
            ),
        )

    @staticmethod
    def _score(candidate: BuildCandidate) -> float:
        speed = max(0.0, 12.0 - candidate.estimated_hours)
        novelty = max(0.0, 1.0 - candidate.duplicate_score) * 10.0
        cost_penalty = min(candidate.estimated_cost_usd / 10.0, 10.0)
        complexity_penalty = candidate.complexity_points / 10.0
        return round(speed + novelty - cost_penalty - complexity_penalty, 3)

    @staticmethod
    def _decision_rank(decision) -> int:
        order = {
            "pass": 0,
            "needs_approval": 1,
            "reject": 2,
            "block": 3,
        }
        return order[str(decision)]
