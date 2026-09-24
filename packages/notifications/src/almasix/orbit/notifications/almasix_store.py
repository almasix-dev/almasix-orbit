"""Orbit bell store backed by Almasix's Laravel-shaped ``notifications`` table."""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any, TypeVar

from almasix.orbit.notifications.store import StoredNotification, _normalize_created_at

T = TypeVar("T")

_ORBIT_TYPE = "almasix.orbit.notifications.Notification"
_UI_KEYS = (
    "title",
    "body",
    "status",
    "icon",
    "icon_color",
    "color",
    "actions",
)


def _run_async(coro: Coroutine[Any, Any, T]) -> T:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda: asyncio.run(coro)).result()


def _notifiable_type(notifiable: Any) -> str:
    try:
        from almasix.notifications.database import notifiable_type

        return notifiable_type(notifiable)
    except ImportError:
        return f"{type(notifiable).__module__}.{type(notifiable).__qualname__}"


def _notifiable_id(notifiable: Any) -> str:
    try:
        from almasix.notifications.database import notifiable_id

        return notifiable_id(notifiable)
    except ImportError:
        key = getattr(notifiable, "get_key", None)
        if callable(key):
            return str(key())
        return str(getattr(notifiable, "id", notifiable))


def _morph(notifiable: Any) -> tuple[str, str]:
    return _notifiable_type(notifiable), _notifiable_id(notifiable)


def _payload_to_data(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("data") or {}
    data = dict(raw) if isinstance(raw, dict) else {}
    for key in _UI_KEYS:
        if key in payload and payload[key] is not None:
            data[key] = payload[key]
    if "title" not in data:
        data["title"] = str(payload.get("title") or "Notification")
    if "status" not in data:
        data["status"] = str(payload.get("status") or "info")
    if "actions" in data and not isinstance(data["actions"], list):
        data["actions"] = []
    return data


def _parse_data(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, str):
        try:
            value = json.loads(raw)
        except (TypeError, ValueError):
            return {}
        return value if isinstance(value, dict) else {}
    return {}


def _row_to_stored(row: dict[str, Any]) -> StoredNotification:
    data = _parse_data(row.get("data"))
    actions = data.get("actions") or []
    if not isinstance(actions, list):
        actions = []
    read_at = row.get("read_at")
    return StoredNotification(
        id=str(row.get("id") or uuid.uuid4()),
        title=str(data.get("title") or "Notification"),
        body=data.get("body"),
        status=str(data.get("status") or "info"),
        icon=data.get("icon"),
        icon_color=data.get("icon_color"),
        color=data.get("color"),
        actions=list(actions),
        read=read_at is not None and str(read_at) not in ("", "None"),
        user_key=str(row.get("notifiable_id") or "") or None,
        data={k: v for k, v in data.items() if k not in _UI_KEYS},
        created_at=_normalize_created_at(row.get("created_at")),
    )


class AlmasixDatabaseNotificationStore:
    """Persist the panel bell in Almasix ``notifications`` (Filament-style).

    Requires ``smith notifications:table`` + migrate (or ``ensure_tables()``).
    Orbit UI fields live in the JSON ``data`` column; morph columns identify
    the recipient the same way as ``almasix.notifications.Notifiable``.
    """

    def save(self, payload: dict[str, Any], *, user: Any = None) -> StoredNotification:
        return _run_async(self._save(payload, user=user))

    def mark_read(self, notification_id: str, *, user: Any = None) -> None:
        _run_async(self._mark_read(notification_id, user=user))

    def mark_unread(self, notification_id: str, *, user: Any = None) -> None:
        _run_async(self._mark_unread(notification_id, user=user))

    def mark_all_read(self, *, user: Any = None) -> None:
        _run_async(self._mark_all_read(user=user))

    def get_for_user(self, user: Any = None) -> list[StoredNotification]:
        return _run_async(self._get_for_user(user=user))

    async def _save(self, payload: dict[str, Any], *, user: Any = None) -> StoredNotification:
        from almasix.orm import DB

        if user is None:

            class _Guest:
                id = "guest"

            user = _Guest()

        data = _payload_to_data(payload)
        nid = str(payload.get("id") or uuid.uuid4())
        ntype, nkey = _morph(user)
        now = datetime.now(UTC)
        want_read = bool(payload.get("read", False))
        row_payload = {
            "id": nid,
            "type": _ORBIT_TYPE,
            "notifiable_type": ntype,
            "notifiable_id": nkey,
            "data": json.dumps(data),
            "read_at": now if want_read else None,
            "created_at": now,
            "updated_at": now,
        }
        existing = await DB.table("notifications").where("id", nid).first()
        if existing is not None:
            created = existing.get("created_at") or now
            await (
                DB.table("notifications")
                .where("id", nid)
                .update(
                    {
                        "type": _ORBIT_TYPE,
                        "notifiable_type": ntype,
                        "notifiable_id": nkey,
                        "data": json.dumps(data),
                        "read_at": now if want_read else None,
                        "updated_at": now,
                        "created_at": created,
                    }
                )
            )
        else:
            await DB.table("notifications").insert(row_payload)
        row = await DB.table("notifications").where("id", nid).first()
        assert row is not None
        return _row_to_stored(dict(row))

    async def _owned(self, notification_id: str, user: Any | None) -> bool:
        if user is None:
            return True
        from almasix.orm import DB

        ntype, nid = _morph(user)
        row = await (
            DB.table("notifications")
            .where("id", notification_id)
            .where("notifiable_type", ntype)
            .where("notifiable_id", nid)
            .first()
        )
        return row is not None

    async def _mark_read(self, notification_id: str, *, user: Any = None) -> None:
        from almasix.orm import DB

        if not await self._owned(notification_id, user):
            return
        now = datetime.now(UTC)
        await (
            DB.table("notifications")
            .where("id", notification_id)
            .update({"read_at": now, "updated_at": now})
        )

    async def _mark_unread(self, notification_id: str, *, user: Any = None) -> None:
        from almasix.orm import DB

        if not await self._owned(notification_id, user):
            return
        now = datetime.now(UTC)
        await (
            DB.table("notifications")
            .where("id", notification_id)
            .update({"read_at": None, "updated_at": now})
        )

    async def _mark_all_read(self, *, user: Any = None) -> None:
        from almasix.orm import DB

        now = datetime.now(UTC)
        query = DB.table("notifications").where_null("read_at")
        if user is not None:
            ntype, nid = _morph(user)
            query = query.where("notifiable_type", ntype).where("notifiable_id", nid)
        await query.update({"read_at": now, "updated_at": now})

    async def _get_for_user(self, user: Any = None) -> list[StoredNotification]:
        from almasix.orm import DB

        query = DB.table("notifications").order_by("created_at", "desc")
        if user is not None:
            ntype, nid = _morph(user)
            query = query.where("notifiable_type", ntype).where("notifiable_id", nid)
        rows = await query.get()
        return [_row_to_stored(dict(r)) for r in rows]
