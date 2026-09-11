from __future__ import annotations

from dataclasses import dataclass

from .models import BuildCandidate, RuntimeState


@dataclass(frozen=True, slots=True)
class AllocationSettings:
    minimum_balance_usd: float = 10.0
    max_autonomous_balance_fraction: float = 0.10
    estimate_headroom: float = 1.25
    max_hours: float = 10.0


@dataclass(frozen=True, slots=True)
class ResourceEnvelope:
    max_cost_usd: float
    max_hours: float
    estimate_fits: bool
    reason: str


class ResourceAllocator:
    """Caps autonomous resources so one agent cannot consume the whole budget."""

    def __init__(self, settings: AllocationSettings | None = None) -> None:
        self.settings = settings or AllocationSettings()

    def allocate(self, candidate: BuildCandidate, state: RuntimeState) -> ResourceEnvelope:
        spendable = max(0.0, state.available_balance_usd - self.settings.minimum_balance_usd)
        balance_cap = spendable * self.settings.max_autonomous_balance_fraction
        estimate_cap = max(0.0, candidate.estimated_cost_usd * self.settings.estimate_headroom)

        caps = [balance_cap, estimate_cap]
        net_value = candidate.probability_weighted_net_value_usd
        if net_value is not None:
            caps.append(max(0.0, net_value + candidate.estimated_cost_usd))

        max_cost = round(min(caps), 2) if caps else 0.0
        max_hours = round(min(self.settings.max_hours, candidate.estimated_hours * 1.25), 2)
        estimate_fits = candidate.estimated_cost_usd <= max_cost

        reason = (
            "estimate fits bounded autonomous envelope"
            if estimate_fits
            else "estimated cost exceeds autonomous envelope; escalate rather than silently expanding budget"
        )
        return ResourceEnvelope(max_cost, max_hours, estimate_fits, reason)
