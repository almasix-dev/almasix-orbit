"""Pluggable database notification store (in-memory default)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4


def utc_now_iso() -> str:
    """UTC timestamp suitable for JSON / SQLite (``YYYY-MM-DDTHH:MM:SSZ``)."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_created_at(value: Any) -> str:
    if value is None or value == "":
        return utc_now_iso()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = str(value).strip()
    return text or utc_now_iso()


def _created_at_sort_key(row: StoredNotification) -> str:
    return str(row.created_at or "")


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
    created_at: str = field(default_factory=utc_now_iso)

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
            "created_at": self.created_at,
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
            created_at=_normalize_created_at(payload.get("created_at")),
        )
        # Upsert by id so re-saves keep a stable list position via created_at.
        self._rows = [r for r in self._rows if r.id != row.id]
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
            rows = list(self._rows)
        else:
            rows = [row for row in self._rows if row.user_key == key]
        return sorted(rows, key=_created_at_sort_key, reverse=True)

    def clear(self) -> None:
        self._rows.clear()


def _decode_json(raw: Any, default: Any) -> Any:
    if raw in (None, ""):
        return default
    if not isinstance(raw, str):
        return default
    try:
        import json

        value = json.loads(raw)
    except (TypeError, ValueError):
        return default
    if isinstance(default, list):
        return value if isinstance(value, list) else default
    if isinstance(default, dict):
        return value if isinstance(value, dict) else default
    return value


class SqliteNotificationStore:
    """SQLite-backed :class:`DatabaseNotificationStore` (stdlib ``sqlite3``).

    Pass ``':memory:'`` for tests, or a file path so the panel bell survives
    process restarts. Rows upsert on ``id``. Listed newest-first by
    ``created_at``.
    """

    def __init__(self, path: str = "orbit-notifications.sqlite") -> None:
        import sqlite3

        self.path = path
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orbit_notifications (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT,
                status TEXT,
                icon TEXT,
                icon_color TEXT,
                color TEXT,
                actions TEXT,
                read INTEGER NOT NULL DEFAULT 0,
                user_key TEXT,
                data TEXT,
                created_at TEXT
            )
            """
        )
        self._ensure_created_at_column()
        self._conn.commit()

    def _ensure_created_at_column(self) -> None:
        cols = {
            str(row[1])
            for row in self._conn.execute("PRAGMA table_info(orbit_notifications)").fetchall()
        }
        if "created_at" not in cols:
            self._conn.execute(
                "ALTER TABLE orbit_notifications ADD COLUMN created_at TEXT"
            )

    def save(self, payload: dict[str, Any], *, user: Any = None) -> StoredNotification:
        import json

        actions = payload.get("actions") or []
        if not isinstance(actions, list):
            actions = []
        data = payload.get("data") or {}
        if not isinstance(data, dict):
            data = {}
        existing_created: str | None = None
        nid = payload.get("id")
        if nid:
            found = self._conn.execute(
                "SELECT created_at FROM orbit_notifications WHERE id = ?",
                (str(nid),),
            ).fetchone()
            if found is not None and found["created_at"]:
                existing_created = str(found["created_at"])
        created = (
            _normalize_created_at(payload["created_at"])
            if payload.get("created_at")
            else (existing_created or utc_now_iso())
        )
        row = StoredNotification(
            id=str(payload.get("id") or uuid4()),
            title=str(payload.get("title") or "Notification"),
            body=payload.get("body"),
            status=str(payload.get("status") or "info"),
            icon=payload.get("icon"),
            icon_color=payload.get("icon_color"),
            color=payload.get("color"),
            actions=list(actions),
            read=bool(payload.get("read", False)),
            user_key=user_key(user),
            data=dict(data),
            created_at=created,
        )
        self._conn.execute(
            """
            INSERT OR REPLACE INTO orbit_notifications
                (id, title, body, status, icon, icon_color, color, actions, read, user_key, data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.id,
                row.title,
                row.body,
                row.status,
                row.icon,
                row.icon_color,
                row.color,
                json.dumps(row.actions),
                1 if row.read else 0,
                row.user_key,
                json.dumps(row.data),
                row.created_at,
            ),
        )
        self._conn.commit()
        return row

    def mark_read(self, notification_id: str, *, user: Any = None) -> None:
        self._set_read(notification_id, True, user=user)

    def mark_unread(self, notification_id: str, *, user: Any = None) -> None:
        self._set_read(notification_id, False, user=user)

    def _set_read(self, notification_id: str, read: bool, *, user: Any = None) -> None:
        key = user_key(user)
        flag = 1 if read else 0
        if key is None:
            self._conn.execute(
                "UPDATE orbit_notifications SET read = ? WHERE id = ?",
                (flag, notification_id),
            )
        else:
            self._conn.execute(
                "UPDATE orbit_notifications SET read = ? WHERE id = ? AND user_key = ?",
                (flag, notification_id, key),
            )
        self._conn.commit()

    def mark_all_read(self, *, user: Any = None) -> None:
        key = user_key(user)
        if key is None:
            self._conn.execute("UPDATE orbit_notifications SET read = 1")
        else:
            self._conn.execute(
                "UPDATE orbit_notifications SET read = 1 WHERE user_key = ?",
                (key,),
            )
        self._conn.commit()

    def get_for_user(self, user: Any = None) -> list[StoredNotification]:
        key = user_key(user)
        if key is None:
            records = self._conn.execute(
                "SELECT * FROM orbit_notifications ORDER BY created_at DESC, id DESC"
            ).fetchall()
        else:
            records = self._conn.execute(
                "SELECT * FROM orbit_notifications WHERE user_key = ? "
                "ORDER BY created_at DESC, id DESC",
                (key,),
            ).fetchall()
        return [self._from_sql(record) for record in records]

    def clear(self) -> None:
        self._conn.execute("DELETE FROM orbit_notifications")
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def _from_sql(self, record: Any) -> StoredNotification:
        keys = record.keys() if hasattr(record, "keys") else ()
        created = record["created_at"] if "created_at" in keys else None
        return StoredNotification(
            id=str(record["id"]),
            title=str(record["title"] or "Notification"),
            body=record["body"],
            status=str(record["status"] or "info"),
            icon=record["icon"],
            icon_color=record["icon_color"],
            color=record["color"],
            actions=_decode_json(record["actions"], []),
            read=bool(record["read"]),
            user_key=record["user_key"],
            data=_decode_json(record["data"], {}),
            # Missing timestamps sort last when listing newest-first.
            created_at=str(created).strip() if created else "",
        )
