"""Action logging utilities for FSM workflows."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ActionType(str, Enum):
    """Required actions that must always be logged."""

    TICKET_CREATION = "ticket_creation"
    ASSIGNMENT_CHANGE = "assignment_change"
    BILLING = "billing"
    STATUS_UPDATE = "status_update"
    GPS_LOG = "gps_log"


@dataclass(slots=True)
class ActionLogEntry:
    """Structured representation of one action log event."""

    action_type: ActionType
    details: dict[str, Any]
    actor_id: str
    timestamp_utc: str

    @classmethod
    def create(cls, action_type: ActionType, details: dict[str, Any], actor_id: str) -> "ActionLogEntry":
        return cls(
            action_type=action_type,
            details=details,
            actor_id=actor_id,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["action_type"] = self.action_type.value
        return payload


class ActionLogger:
    """In-memory logger that records all required action categories."""

    def __init__(self) -> None:
        self._entries: list[ActionLogEntry] = []

    def log(self, action_type: ActionType, details: dict[str, Any], actor_id: str) -> ActionLogEntry:
        entry = ActionLogEntry.create(action_type=action_type, details=details, actor_id=actor_id)
        self._entries.append(entry)
        return entry

    def all_entries(self) -> list[ActionLogEntry]:
        return list(self._entries)
