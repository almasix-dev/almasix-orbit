"""Panel JSON endpoints for the database bell and live broadcast hub."""

from __future__ import annotations

from typing import Any


def _panel_suffix_url(panel: Any, suffix: str) -> str:
    getter = getattr(panel, "get_path", None)
    path = str(getter() if callable(getter) else "") if panel is not None else ""
    prefix = path.rstrip("/")
    if not prefix or prefix == "/":
        return f"/{suffix}"
    return f"{prefix}/{suffix}"


def panel_live_url(panel: Any) -> str:
    return _panel_suffix_url(panel, "orbit-live")


def panel_notifications_url(panel: Any) -> str:
    return _panel_suffix_url(panel, "orbit-notifications")


async def read_json_body(request: Any) -> dict[str, Any]:
    """Best-effort JSON object from a framework request."""
    if request is None:
        return {}
    for name in ("json", "json_body"):
        getter = getattr(request, name, None)
        if callable(getter):
            try:
                data = getter()
                if hasattr(data, "__await__"):
                    data = await data
                return dict(data) if isinstance(data, dict) else {}
            except Exception:
                return {}
    body = getattr(request, "body", None)
    if isinstance(body, (bytes, bytearray, str)) and body:
        import json

        try:
            raw = body.decode() if isinstance(body, (bytes, bytearray)) else body
            data = json.loads(raw)
            return dict(data) if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def handle_live_broadcasts(
    panel: Any,
    *,
    since: str | int | None = 0,
) -> dict[str, Any]:
    try:
        cursor = int(since)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        cursor = 0
    if cursor < 0:
        cursor = 0
    hub = None
    getter = getattr(panel, "get_broadcast_hub", None)
    if callable(getter):
        try:
            hub = getter()
        except Exception:
            hub = None
    if hub is None:
        hub = getattr(panel, "_broadcast_hub", None)
    since_fn = getattr(hub, "since", None) if hub is not None else None
    events: list[dict[str, Any]] = []
    if callable(since_fn):
        try:
            events = list(since_fn(cursor))
        except Exception:
            events = []
    return {"events": events, "cursor": cursor + len(events)}


def handle_database_notifications(
    panel: Any,
    *,
    user: Any = None,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    store = None
    getter = getattr(panel, "get_notification_store", None)
    if callable(getter):
        try:
            store = getter()
        except Exception:
            store = None
    if store is None:
        store = getattr(panel, "_database_notification_store", None)
    verb = str(method or "GET").upper()
    body = payload or {}
    if verb == "POST" and store is not None:
        try:
            if body.get("all"):
                store.mark_all_read(user=user)
            elif body.get("id"):
                nid = str(body["id"])
                if body.get("read") is False:
                    store.mark_unread(nid, user=user)
                else:
                    store.mark_read(nid, user=user)
        except Exception:
            pass
    notes: list[dict[str, Any]] = []
    if store is not None:
        try:
            notes = [row.to_dict() for row in store.get_for_user(user)]
        except Exception:
            notes = []
    if not notes:
        seeds = getattr(panel, "_database_notifications", []) or []
        notes = [dict(item) for item in seeds]
    notes = sort_notifications_latest_first(notes)
    return {"notifications": notes, "ok": True}


def sort_notifications_latest_first(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Stable newest-first order for store rows and panel seeds."""

    def key(row: dict[str, Any]) -> tuple[str, str]:
        created = str(row.get("created_at") or "")
        nid = str(row.get("id") or "")
        return (created, nid)

    return sorted(notes, key=key, reverse=True)
