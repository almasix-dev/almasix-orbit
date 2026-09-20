"""Pluggable database notification store (in-memory default)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4


@dataclass
class StoredNotification:
    """Persisted database notification row."""

    id: str
    title: str
    body: str | None = None
    status: str = "info"
    icon: str | None = None
    icon_color: str | None = None
    color: str | None = None
    actions: list[dict[str, Any]] = field(default_factory=list)
    read: bool = False
    user_key: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "status": self.status,
            "icon": self.icon,
            "icon_color": self.icon_color,
            "color": self.color,
            "actions": list(self.actions),
            "read": self.read,
            "user_key": self.user_key,
            "data": dict(self.data),
        }


def user_key(user: Any | None) -> str | None:
    if user is None:
        return None
    for attr in ("id", "pk", "email", "name"):
        value = getattr(user, attr, None)
        if value is not None:
            return str(value)
    return str(user)


@runtime_checkable
class DatabaseNotificationStore(Protocol):
    """App-provided persistence for database notifications."""

    def save(
        self,
        payload: dict[str, Any],
        *,
        user: Any = None,
    ) -> StoredNotification: ...  # pragma: no cover

    def mark_read(self, notification_id: str, *, user: Any = None) -> None: ...  # pragma: no cover

    def mark_unread(self, notification_id: str, *, user: Any = None) -> None: ...  # pragma: no cover

    def mark_all_read(self, *, user: Any = None) -> None: ...  # pragma: no cover

    def get_for_user(self, user: Any = None) -> list[StoredNotification]: ...  # pragma: no cover


class InMemoryDatabaseNotificationStore:
    """Process-local store — enough for demos and tests without migrations."""

    def __init__(self) -> None:
        self._rows: list[StoredNotification] = []

    def save(self, payload: dict[str, Any], *, user: Any = None) -> StoredNotification:
        row = StoredNotification(
            id=str(payload.get("id") or uuid4()),
            title=str(payload.get("title") or "Notification"),
            body=payload.get("body"),
            status=str(payload.get("status") or "info"),
            icon=payload.get("icon"),
            icon_color=payload.get("icon_color"),
            color=payload.get("color"),
            actions=list(payload.get("actions") or []),
            read=bool(payload.get("read", False)),
            user_key=user_key(user),
            data=dict(payload.get("data") or {}),
        )
        self._rows.append(row)
        return row

    def mark_read(self, notification_id: str, *, user: Any = None) -> None:
        key = user_key(user)
        for row in self._rows:
            if row.id == notification_id and (key is None or row.user_key == key):
                row.read = True

    def mark_unread(self, notification_id: str, *, user: Any = None) -> None:
        key = user_key(user)
        for row in self._rows:
            if row.id == notification_id and (key is None or row.user_key == key):
                row.read = False

    def mark_all_read(self, *, user: Any = None) -> None:
        key = user_key(user)
        for row in self._rows:
            if key is None or row.user_key == key:
                row.read = True

    def get_for_user(self, user: Any = None) -> list[StoredNotification]:
        key = user_key(user)
        if key is None:
            return list(self._rows)
        return [row for row in self._rows if row.user_key == key]

    def clear(self) -> None:
        self._rows.clear()
