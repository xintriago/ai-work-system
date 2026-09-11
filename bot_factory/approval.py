from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum


class ApprovalOutcome(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    request_id: str
    action: str
    target: str
    environment: str
    external_effect: str
    max_cost_usd: float
    data_exposed: str
    rollback: str
    evidence: str

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_text(self) -> str:
        return (
            "APPROVAL REQUEST\n"
            f"ID: {self.request_id}\n"
            f"Action: {self.action}\n"
            f"Target/environment: {self.target} / {self.environment}\n"
            f"External effect: {self.external_effect}\n"
            f"Cost or maximum loss: ${self.max_cost_usd:.2f}\n"
            f"Data exposed: {self.data_exposed}\n"
            f"Rollback/cancellation: {self.rollback}\n"
            f"Evidence reviewed: {self.evidence}\n"
            f"Fingerprint: {self.fingerprint[:12]}\n"
            "Approve? YES / NO"
        )


@dataclass(frozen=True, slots=True)
class ApprovalToken:
    request_id: str
    request_fingerprint: str
    outcome: ApprovalOutcome


class ApprovalGuard:
    """Prevents stale or broad approvals from authorizing a changed action."""

    @staticmethod
    def issue(request: ApprovalRequest, outcome: ApprovalOutcome) -> ApprovalToken:
        return ApprovalToken(
            request_id=request.request_id,
            request_fingerprint=request.fingerprint,
            outcome=outcome,
        )

    @staticmethod
    def validates(request: ApprovalRequest, token: ApprovalToken) -> bool:
        return (
            token.outcome is ApprovalOutcome.APPROVED
            and token.request_id == request.request_id
            and token.request_fingerprint == request.fingerprint
        )
