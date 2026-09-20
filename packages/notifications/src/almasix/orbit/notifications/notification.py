"""Notifications — flash, database, and broadcast channels (Filament 5 parity)."""

from __future__ import annotations

import contextvars
from collections.abc import Sequence
from enum import StrEnum
from typing import Any, Self
from uuid import uuid4

from almasix.orbit.notifications.actions import NotificationAction
from almasix.orbit.notifications.alignment import Notifications
from almasix.orbit.notifications.broadcast import get_broadcast_hub
from almasix.orbit.notifications.store import (
    DatabaseNotificationStore,
    InMemoryDatabaseNotificationStore,
    StoredNotification,
    user_key,
)
from almasix.orbit.support.html import e

try:
    from almasix.orbit.support.icons import render_icon
except ImportError:  # pragma: no cover

    def render_icon(name: str, *, size: int = 20, css_class: str = "or-icon") -> str:
        return f'<span class="{e(css_class)}" data-icon="{e(name)}"></span>'


class NotificationStatus(StrEnum):
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"


_STATUS_ICONS: dict[NotificationStatus, str] = {
    NotificationStatus.SUCCESS: "heroicon-o-check-circle",
    NotificationStatus.WARNING: "heroicon-o-exclamation-triangle",
    NotificationStatus.DANGER: "heroicon-o-x-circle",
    NotificationStatus.INFO: "heroicon-o-information-circle",
}

_ATTR_ALIASES = {
    "id": "_id",
    "title": "_title",
    "body": "_body",
    "status": "_status",
    "icon": "_icon",
    "icon_color": "_icon_color",
    "color": "_color",
    "duration": "_duration",
    "persistent": "_persistent",
    "channel": "_channel",
    "actions": "_actions",
    "read": "_read",
    "recipient": "_recipient",
}

_default_notifier: contextvars.ContextVar[Any] = contextvars.ContextVar(
    "orbit_default_notifier",
    default=None,
)
_process_notifier: Notifier | None = None


def get_notifier() -> Notifier:
    """Return the context-local notifier, else the process-global default."""
    current = _default_notifier.get()
    if current is not None:
        return current  # type: ignore[no-any-return]
    global _process_notifier
    if _process_notifier is None:
        _process_notifier = Notifier()
    return _process_notifier


def set_notifier(notifier: Notifier | None) -> contextvars.Token[Any]:
    """Bind a notifier for the current context (tests / request scope)."""
    return _default_notifier.set(notifier)


def reset_process_notifier() -> Notifier:
    """Replace the process-global default notifier (tests)."""
    global _process_notifier
    _process_notifier = Notifier()
    return _process_notifier


class Notification:
    """Fluent flash / database / broadcast notification.

    Build with Filament-style chains (``.title().success().send()``). After the
    chain, field values are readable as attributes (``note.title``,
    ``note.status``, …) because fluent methods write instance attributes that
    shadow the class methods.
    """

    def __init__(self) -> None:
        object.__setattr__(self, "_id", str(uuid4()))
        object.__setattr__(self, "_title", "")
        object.__setattr__(self, "_body", None)
        object.__setattr__(self, "_status", NotificationStatus.INFO)
        object.__setattr__(self, "_icon", None)
        object.__setattr__(self, "_icon_explicit", False)
        object.__setattr__(self, "_icon_color", None)
        object.__setattr__(self, "_color", None)
        object.__setattr__(self, "_duration", 6000)
        object.__setattr__(self, "_persistent", False)
        object.__setattr__(self, "_channel", "flash")
        object.__setattr__(self, "_actions", [])
        object.__setattr__(self, "_recipient", None)
        object.__setattr__(self, "_read", False)

    def __getattr__(self, name: str) -> Any:
        private = _ATTR_ALIASES.get(name)
        if private is not None and private in self.__dict__:
            return self.__dict__[private]
        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        private = _ATTR_ALIASES.get(name, name)
        object.__setattr__(self, private if private.startswith("_") else name, value)

    @classmethod
    def make(
        cls,
        custom_id: str | None = None,
        /,
        *,
        title: str | None = None,
        id: str | None = None,
    ) -> Self:
        """Create a notification.

        * ``make()`` — empty, random id
        * ``make("greeting")`` — custom id (Filament)
        * ``make(title="Saved")`` — set title
        * ``make("Post saved")`` — legacy Orbit title when the string contains a space
        """
        inst = cls()
        if id is not None:
            object.__setattr__(inst, "_id", str(id))
        if custom_id is not None:
            if title is not None or id is not None:
                object.__setattr__(inst, "_id", str(custom_id))
            elif " " in custom_id:
                object.__setattr__(inst, "_title", custom_id)
                object.__setattr__(inst, "title", custom_id)
            else:
                object.__setattr__(inst, "_id", str(custom_id))
                object.__setattr__(inst, "id", str(custom_id))
        if title is not None:
            object.__setattr__(inst, "_title", title)
            object.__setattr__(inst, "title", title)
        if id is not None:
            object.__setattr__(inst, "id", str(id))
        return inst

    def get_id(self) -> str:
        return str(self._id)

    def set_id(self, value: str) -> Self:
        object.__setattr__(self, "_id", value)
        return self

    def title(self, value: str) -> Self:
        object.__setattr__(self, "_title", value)
        # Shadow class method so ``note.title`` reads as the string afterwards.
        object.__setattr__(self, "title", value)
        return self

    def body(self, text: str) -> Self:
        object.__setattr__(self, "_body", text)
        object.__setattr__(self, "body", text)
        return self

    def body_text(self, text: str) -> Self:
        """Alias for :meth:`body` (Orbit ≤0.3)."""
        return self.body(text)

    def icon(self, name: str | None) -> Self:
        object.__setattr__(self, "_icon", name)
        object.__setattr__(self, "_icon_explicit", True)
        object.__setattr__(self, "icon", name)
        return self

    def icon_color(self, value: str | None) -> Self:
        object.__setattr__(self, "_icon_color", value)
        object.__setattr__(self, "icon_color", value)
        return self

    def color(self, value: str | None) -> Self:
        object.__setattr__(self, "_color", value)
        object.__setattr__(self, "color", value)
        return self

    def status(self, value: NotificationStatus | str) -> Self:
        resolved = NotificationStatus(str(value))
        object.__setattr__(self, "_status", resolved)
        object.__setattr__(self, "status", resolved)
        if not self._icon_explicit:
            object.__setattr__(self, "_icon", _STATUS_ICONS.get(resolved))
            object.__setattr__(self, "icon", _STATUS_ICONS.get(resolved))
        if self._icon_color is None:
            object.__setattr__(self, "_icon_color", resolved.value)
            object.__setattr__(self, "icon_color", resolved.value)
        if self._color is None:
            object.__setattr__(self, "_color", resolved.value)
            object.__setattr__(self, "color", resolved.value)
        return self

    def success(self) -> Self:
        return self.status(NotificationStatus.SUCCESS)

    def warning(self) -> Self:
        return self.status(NotificationStatus.WARNING)

    def danger(self) -> Self:
        return self.status(NotificationStatus.DANGER)

    def info(self) -> Self:
        return self.status(NotificationStatus.INFO)

    def duration(self, ms: int) -> Self:
        object.__setattr__(self, "_duration", int(ms))
        object.__setattr__(self, "duration", int(ms))
        return self

    def seconds(self, n: int | float) -> Self:
        return self.duration(int(float(n) * 1000))

    def persistent(self, condition: bool = True) -> Self:
        object.__setattr__(self, "_persistent", bool(condition))
        object.__setattr__(self, "persistent", bool(condition))
        return self

    def persistent_mode(self, condition: bool = True) -> Self:
        """Alias for :meth:`persistent` (Orbit ≤0.3)."""
        return self.persistent(condition)

    def actions(self, items: Sequence[NotificationAction | dict[str, Any]]) -> Self:
        out: list[NotificationAction] = []
        for item in items:
            if isinstance(item, NotificationAction):
                out.append(item)
                continue
            action = NotificationAction.make(str(item.get("name") or "action"))
            if item.get("label"):
                action.label(str(item["label"]))
            if item.get("button"):
                action.button()
            if item.get("url"):
                action.url(str(item["url"]))
            if item.get("open_url_in_new_tab"):
                action.open_url_in_new_tab()
            if item.get("dispatch"):
                action.dispatch(
                    str(item["dispatch"]),
                    list(item.get("dispatch_payload") or []),
                )
            if item.get("close"):
                action.close()
            if item.get("color"):
                action.color(str(item["color"]))
            if item.get("mark_as_read"):
                action.mark_as_read()
            if item.get("mark_as_unread"):
                action.mark_as_unread()
            out.append(action)
        object.__setattr__(self, "_actions", out)
        object.__setattr__(self, "actions", out)
        return self

    def send(self) -> Self:
        object.__setattr__(self, "_channel", "flash")
        object.__setattr__(self, "channel", "flash")
        get_notifier().send(self)
        return self

    def send_to_database(
        self,
        user: Any = None,
        *,
        is_event_dispatched: bool = False,
    ) -> Self:
        object.__setattr__(self, "_channel", "database")
        object.__setattr__(self, "channel", "database")
        object.__setattr__(self, "_recipient", user)
        get_notifier().send_to_database(
            self,
            user=user,
            is_event_dispatched=is_event_dispatched,
        )
        return self

    def to_database(self) -> Self:
        object.__setattr__(self, "_channel", "database")
        object.__setattr__(self, "channel", "database")
        return self

    def broadcast(self, user: Any = None) -> Self:
        object.__setattr__(self, "_channel", "broadcast")
        object.__setattr__(self, "channel", "broadcast")
        object.__setattr__(self, "_recipient", user)
        get_notifier().broadcast_send(self, user=user)
        return self

    def to_broadcast(self) -> Self:
        object.__setattr__(self, "_channel", "broadcast")
        object.__setattr__(self, "channel", "broadcast")
        return self

    def to_dict(self) -> dict[str, Any]:
        status = self._status
        status_val = status.value if isinstance(status, NotificationStatus) else str(status)
        return {
            "id": self._id,
            "title": self._title,
            "body": self._body,
            "status": status_val,
            "icon": self._icon,
            "icon_color": self._icon_color,
            "color": self._color,
            "duration": self._duration,
            "persistent": self._persistent,
            "channel": self._channel,
            "actions": [a.to_dict() for a in self._actions],
            "read": self._read,
        }

    def render(self) -> str:
        data = self.to_dict()
        status = data["status"]
        color = data["color"] or status
        icon_html = ""
        if data["icon"]:
            icon_html = (
                f'<span class="or-notification-icon '
                f'or-notification-icon-{e(str(data["icon_color"] or color))}">'
                f"{render_icon(str(data['icon']), size=20, css_class='or-icon')}</span>"
            )
        body = (
            f'<div class="or-notification-body">{e(data["body"])}</div>'
            if data["body"]
            else ""
        )
        actions_html = ""
        if self._actions:
            actions_html = (
                '<div class="or-notification-actions">'
                + "".join(a.render() for a in self._actions)
                + "</div>"
            )
        dismiss = (
            '<button type="button" class="or-notification-dismiss" '
            f'@click="dismiss(\'{e(data["id"])}\')" aria-label="Dismiss">'
            f"{render_icon('heroicon-o-x-mark', size=14, css_class='or-icon')}"
            "</button>"
        )
        persistent_attr = "true" if data["persistent"] else "false"
        duration_attr = (
            "" if data["persistent"] else f' data-duration="{int(data["duration"])}"'
        )
        color_class = f" or-notification-color-{e(str(color))}" if color else ""
        return (
            f'<div class="or-notification or-notification-{e(status)}{color_class}" '
            f'data-id="{e(data["id"])}" data-persistent="{persistent_attr}"'
            f'{duration_attr} role="status">'
            f'{icon_html}<div class="or-notification-content">'
            f'<strong class="or-notification-title">{e(data["title"])}</strong>'
            f"{body}{actions_html}</div>{dismiss}</div>"
        )


class Notifier:
    """In-process notification bag with pluggable database store."""

    def __init__(
        self,
        *,
        database_store: DatabaseNotificationStore | None = None,
    ) -> None:
        self._flash: list[Notification] = []
        self._database: list[Notification] = []
        self._broadcast: list[Notification] = []
        self._store: DatabaseNotificationStore = (
            database_store or InMemoryDatabaseNotificationStore()
        )
        self._database_events: list[dict[str, Any]] = []

    @property
    def store(self) -> DatabaseNotificationStore:
        return self._store

    def use_store(self, store: DatabaseNotificationStore) -> Self:
        self._store = store
        return self

    def use_hub(self, hub: Any | None) -> Self:
        self._hub = hub
        return self

    def send(self, notification: Notification) -> Notification:
        channel = notification._channel or "flash"
        if channel == "database":
            return self.send_to_database(
                notification,
                user=notification._recipient,
            )
        if channel == "broadcast":
            return self.broadcast_send(
                notification,
                user=notification._recipient,
            )
        self._flash.append(notification)
        return notification

    def send_to_database(
        self,
        notification: Notification,
        *,
        user: Any = None,
        is_event_dispatched: bool = False,
    ) -> Notification:
        object.__setattr__(notification, "_channel", "database")
        object.__setattr__(notification, "channel", "database")
        if user is not None:
            object.__setattr__(notification, "_recipient", user)
        self._database.append(notification)
        self._store.save(notification.to_dict(), user=user)
        if is_event_dispatched:
            self._database_events.append(
                {
                    "type": "DatabaseNotificationsSent",
                    "user": user,
                    "id": notification.get_id(),
                }
            )
        return notification

    def broadcast_send(
        self,
        notification: Notification,
        *,
        user: Any = None,
    ) -> Notification:
        object.__setattr__(notification, "_channel", "broadcast")
        object.__setattr__(notification, "channel", "broadcast")
        if user is not None:
            object.__setattr__(notification, "_recipient", user)
        self._broadcast.append(notification)
        hub = getattr(self, "_hub", None)
        if hub is None:
            try:
                hub = get_broadcast_hub()
            except Exception:
                hub = None
        publish = getattr(hub, "publish", None) if hub is not None else None
        if callable(publish):
            payload = dict(notification.to_dict())
            if user is not None:
                payload["user_key"] = user_key(user)
            try:
                publish(payload)
            except Exception:
                pass
        return notification

    def flash(self) -> list[Notification]:
        items = list(self._flash)
        self._flash.clear()
        return items

    def peek_flash(self) -> list[Notification]:
        return list(self._flash)

    def database(self) -> list[Notification]:
        return list(self._database)

    def broadcast_queue(self) -> list[Notification]:
        return list(self._broadcast)

    def database_events(self) -> list[dict[str, Any]]:
        return list(self._database_events)

    def clear(self) -> None:
        self._flash.clear()
        self._database.clear()
        self._broadcast.clear()
        self._database_events.clear()
        clear = getattr(self._store, "clear", None)
        if callable(clear):
            clear()

    def render_flash(self) -> str:
        classes = Notifications.host_classes()
        align = Notifications.get_alignment().value
        valign = Notifications.get_vertical_alignment().value
        items = self.flash()
        return (
            f'<div class="{classes}" x-data="orbitNotifications" '
            f'data-alignment="{e(align)}" data-vertical-alignment="{e(valign)}" '
            f'role="region" aria-label="Notifications">'
            + "".join(n.render() for n in items)
            + _toast_host_template()
            + "</div>"
        )

    def render_toast_host(self, *, include_flash: bool = True) -> str:
        """Empty (or flash-seeded) toast host for the panel shell."""
        classes = Notifications.host_classes()
        align = Notifications.get_alignment().value
        valign = Notifications.get_vertical_alignment().value
        body = "".join(n.render() for n in (self.flash() if include_flash else []))
        return (
            f'<div class="{classes}" x-data="orbitNotifications" '
            f'data-alignment="{e(align)}" data-vertical-alignment="{e(valign)}" '
            f'role="region" aria-label="Notifications">{body}'
            f"{_toast_host_template()}</div>"
        )


def _toast_host_template() -> str:
    return (
        '<template x-for="n in notifications" :key="n.id">'
        '<div class="or-notification" '
        ':class="\'or-notification-\' + (n.status || \'info\') + '
        "(n.color ? ' or-notification-color-' + n.color : '')\" "
        ':data-id="n.id" '
        ':data-persistent="n.persistent ? \'true\' : \'false\'" '
        ':data-duration="n.persistent ? null : n.duration" '
        'role="status">'
        '<span class="or-notification-icon" x-show="n.icon" x-text="\'\'"></span>'
        '<div class="or-notification-content">'
        '<strong class="or-notification-title" x-text="n.title"></strong>'
        '<div class="or-notification-body" x-show="n.body" x-text="n.body"></div>'
        '<div class="or-notification-actions" x-show="n.actions && n.actions.length">'
        '<template x-for="a in (n.actions || [])" :key="a.name">'
        '<button type="button" class="or-notification-action or-btn or-btn-sm" '
        '@click="runAction(n.id, a)" x-text="a.label || a.name"></button>'
        "</template></div></div>"
        '<button type="button" class="or-notification-dismiss" '
        '@click="dismiss(n.id)" aria-label="Dismiss">×</button>'
        "</div></template>"
    )


class LiveNotifier(Notifier):
    """Broadcast / live notification host (Alpine + channel subscriptions).

    Pair with a :class:`~almasix.orbit.notifications.broadcast.BroadcastHub`
    and the panel ``/orbit-live`` endpoint so the browser can poll new events
    and dispatch ``orbit:broadcast``.
    """

    def __init__(
        self,
        *,
        database_store: DatabaseNotificationStore | None = None,
    ) -> None:
        super().__init__(database_store=database_store)
        self._channels: set[str] = set()
        self._hub: Any | None = None
        self._live_url: str | None = None
        self._polling_ms: int | None = None

    def channel(self, name: str) -> Self:
        self._channels.add(name)
        return self

    def get_channels(self) -> list[str]:
        return sorted(self._channels)

    def live_url(self, url: str | None) -> Self:
        self._live_url = url
        return self

    def polling(self, milliseconds: int | None) -> Self:
        self._polling_ms = milliseconds
        return self

    def render_live(self) -> str:
        channels = ",".join(self.get_channels())
        attrs = f' data-channels="{e(channels)}"' if channels else ""
        if self._live_url:
            attrs += f' data-orbit-live-url="{e(self._live_url)}"'
        if self._polling_ms:
            attrs += f' data-polling="{int(self._polling_ms)}"'
        return (
            f'<div class="or-live-notifier"{attrs} x-data="orbitLiveNotifications">'
            f"{self.render_toast_host(include_flash=True)}"
            f"</div>"
        )


def notification_from_dict(data: dict[str, Any]) -> Notification:
    """Hydrate a :class:`Notification` from a plain dict (panel seeds / store)."""
    note = Notification.make(id=str(data["id"])) if data.get("id") else Notification.make()
    if data.get("title"):
        note.title(str(data["title"]))
    if data.get("body"):
        note.body(str(data["body"]))
    if data.get("icon"):
        note.icon(str(data["icon"]))
    if data.get("icon_color"):
        note.icon_color(str(data["icon_color"]))
    if data.get("color"):
        note.color(str(data["color"]))
    if data.get("status"):
        # After icon() so status defaults do not overwrite an explicit icon.
        note.status(str(data["status"]))
    if data.get("duration") is not None:
        # status()/icon() may have shadowed fluent methods — use private fields.
        object.__setattr__(note, "_duration", int(data["duration"]))
        object.__setattr__(note, "duration", int(data["duration"]))
    if data.get("persistent"):
        object.__setattr__(note, "_persistent", True)
        object.__setattr__(note, "persistent", True)
    if data.get("actions"):
        Notification.actions(note, list(data["actions"]))
    if data.get("channel"):
        object.__setattr__(note, "_channel", str(data["channel"]))
        object.__setattr__(note, "channel", str(data["channel"]))
    if data.get("read"):
        object.__setattr__(note, "_read", True)
        object.__setattr__(note, "read", True)
    return note


__all__ = [
    "Notification",
    "NotificationAction",
    "NotificationStatus",
    "Notifier",
    "LiveNotifier",
    "Notifications",
    "DatabaseNotificationStore",
    "InMemoryDatabaseNotificationStore",
    "StoredNotification",
    "get_notifier",
    "set_notifier",
    "reset_process_notifier",
    "notification_from_dict",
]
