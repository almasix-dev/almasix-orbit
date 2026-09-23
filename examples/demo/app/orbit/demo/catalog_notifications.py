"""Notify the signed-in panel user when catalog models change."""

from __future__ import annotations

from typing import Any

from almasix.orbit.notifications import Notification


def _current_user() -> Any | None:
    try:
        from almasix.auth import auth

        return auth().user()
    except Exception:
        return None


def notify_catalog(event: str, model: Any) -> None:
    """Persist a database notification for the active user (no-op if guest)."""
    user = _current_user()
    if user is None:
        return
    label = type(model).__name__
    title_attr = getattr(model, "name", None) or getattr(model, "title", None) or getattr(
        model, "id", ""
    )
    name = str(title_attr)
    verb = {"created": "created", "updated": "updated", "deleted": "removed"}.get(
        event, event
    )
    status = {"created": "success", "updated": "info", "deleted": "warning"}.get(
        event, "info"
    )
    (
        Notification.make()
        .title(f"{label} {verb}")
        .body(f"{name} was {verb} in the Orbit Records catalog.")
        .status(status)
        .send_to_database(user, is_event_dispatched=True)
    )


class CatalogNotificationObserver:
    def created(self, model: Any) -> None:
        notify_catalog("created", model)

    def updated(self, model: Any) -> None:
        notify_catalog("updated", model)

    def deleted(self, model: Any) -> None:
        notify_catalog("deleted", model)
