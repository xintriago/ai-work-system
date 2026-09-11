from __future__ import annotations

from dataclasses import dataclass

from .models import (
    ActionClass,
    BuildCandidate,
    Decision,
    Evaluation,
    GateResult,
    RiskLevel,
    RuntimeState,
)


@dataclass(frozen=True, slots=True)
class PolicySettings:
    overnight_hours: float = 10.0
    max_complexity_points: int = 40
    duplicate_threshold: float = 0.82
    minimum_balance_usd: float = 10.0
    minimum_net_value_usd: float = 0.0
    approval_actions: frozenset[ActionClass] = frozenset(
        {
            ActionClass.MERGE,
            ActionClass.DEPLOY,
            ActionClass.EXTERNAL_MESSAGE,
            ActionClass.PAYMENT,
            ActionClass.SECRET_CHANGE,
            ActionClass.DESTRUCTIVE,
        }
    )


class PolicyEngine:
    """Deterministic pre-flight policy; model output cannot bypass these gates."""

    def __init__(self, settings: PolicySettings | None = None) -> None:
        self.settings = settings or PolicySettings()

    def evaluate(self, candidate: BuildCandidate, state: RuntimeState) -> Evaluation:
        gates: list[GateResult] = []

        if candidate.estimated_hours > self.settings.overnight_hours:
            gates.append(
                GateResult(
                    "scope",
                    Decision.REJECT,
                    f"estimated {candidate.estimated_hours:g}h exceeds {self.settings.overnight_hours:g}h work-cycle limit",
                )
            )
        elif candidate.complexity_points > self.settings.max_complexity_points:
            gates.append(
                GateResult(
                    "scope",
                    Decision.REJECT,
                    f"complexity {candidate.complexity_points} exceeds {self.settings.max_complexity_points}",
                )
            )
        else:
            gates.append(GateResult("scope", Decision.PASS, "bounded enough for one work cycle"))

        if candidate.duplicate_score >= self.settings.duplicate_threshold:
            gates.append(
                GateResult(
                    "dupe",
                    Decision.REJECT,
                    f"duplicate score {candidate.duplicate_score:.2f} meets/exceeds {self.settings.duplicate_threshold:.2f}",
                )
            )
        else:
            gates.append(GateResult("dupe", Decision.PASS, "no duplicate threshold hit"))

        net_value = candidate.probability_weighted_net_value_usd
        if net_value is None:
            gates.append(
                GateResult(
                    "value",
                    Decision.PASS,
                    "benefit is not monetized; value gate recorded but not used as a blocker",
                )
            )
        elif net_value <= self.settings.minimum_net_value_usd:
            gates.append(
                GateResult(
                    "value",
                    Decision.REJECT,
                    f"probability-weighted net value ${net_value:.2f} does not exceed ${self.settings.minimum_net_value_usd:.2f}",
                )
            )
        else:
            gates.append(
                GateResult(
                    "value",
                    Decision.PASS,
                    f"probability-weighted net value ${net_value:.2f} remains positive after cost and overhead",
                )
            )

        if not state.last_deploy_healthy:
            gates.append(
                GateResult(
                    "crash",
                    Decision.BLOCK,
                    "last production deploy is unhealthy; repair takes priority",
                )
            )
        else:
            gates.append(GateResult("crash", Decision.PASS, "last deploy healthy"))

        if candidate.risk is RiskLevel.HIGH:
            gates.append(GateResult("risk", Decision.REJECT, "high-risk candidate vetoed"))
        elif candidate.risk is RiskLevel.MEDIUM:
            gates.append(GateResult("risk", Decision.NEEDS_APPROVAL, "medium risk requires owner review"))
        else:
            gates.append(GateResult("risk", Decision.PASS, "risk below veto threshold"))

        projected_balance = state.available_balance_usd - candidate.estimated_cost_usd
        if projected_balance < self.settings.minimum_balance_usd:
            gates.append(
                GateResult(
                    "money",
                    Decision.BLOCK,
                    f"projected balance ${projected_balance:.2f} would breach ${self.settings.minimum_balance_usd:.2f} floor",
                )
            )
        else:
            gates.append(GateResult("money", Decision.PASS, "budget floor preserved"))

        if candidate.action in self.settings.approval_actions and not state.owner_approved:
            gates.append(
                GateResult(
                    "approval",
                    Decision.NEEDS_APPROVAL,
                    f"{candidate.action.value} requires explicit owner approval",
                )
            )
        else:
            gates.append(GateResult("approval", Decision.PASS, "no unresolved deterministic approval gate"))

        final = self._final_decision(gates)
        return Evaluation(candidate=candidate, final_decision=final, gates=tuple(gates))

    @staticmethod
    def _final_decision(gates: list[GateResult]) -> Decision:
        decisions = {gate.decision for gate in gates}
        if Decision.BLOCK in decisions:
            return Decision.BLOCK
        if Decision.REJECT in decisions:
            return Decision.REJECT
        if Decision.NEEDS_APPROVAL in decisions:
            return Decision.NEEDS_APPROVAL
        return Decision.PASS
