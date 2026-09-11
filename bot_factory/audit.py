from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import Evaluation


@dataclass(frozen=True, slots=True)
class AuditEvent:
    run_id: str
    stage: str
    event_type: str
    payload: dict[str, Any]
    timestamp: str

    @classmethod
    def now(
        cls,
        run_id: str,
        stage: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> "AuditEvent":
        return cls(
            run_id=run_id,
            stage=stage,
            event_type=event_type,
            payload=payload,
            timestamp=datetime.now(UTC).isoformat(),
        )


class JsonlAuditWriter:
    """Append-oriented local audit log. Never rewrite prior events."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: AuditEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), sort_keys=True, default=str) + "\n")

    def append_evaluation(self, run_id: str, stage: str, evaluation: Evaluation) -> None:
        payload = {
            "candidate": evaluation.candidate.name,
            "final_decision": evaluation.final_decision.value,
            "gates": [
                {
                    "gate": gate.gate,
                    "decision": gate.decision.value,
                    "reason": gate.reason,
                }
                for gate in evaluation.gates
            ],
        }
        self.append(AuditEvent.now(run_id, stage, "policy_evaluation", payload))
