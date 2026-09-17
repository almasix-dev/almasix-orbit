
"""Notifications — flash, database, and broadcast channels."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Self
from uuid import uuid4

from almasix.orbit.support.html import e


class NotificationStatus(StrEnum):
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"


@dataclass
class Notification:
    title: str
    body: str | None = None
    status: NotificationStatus = NotificationStatus.INFO
    icon: str | None = None
    duration: int = 6000
    id: str = field(default_factory=lambda: str(uuid4()))
    persistent: bool = False
    channel: str = "flash"  # flash | database | broadcast
    actions: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def make(cls, title: str) -> Notification:
        return cls(title=title)

    def body_text(self, text: str) -> Self:
        self.body = text
        return self

    def success(self) -> Self:
        self.status = NotificationStatus.SUCCESS
        return self

    def warning(self) -> Self:
        self.status = NotificationStatus.WARNING
        return self

    def danger(self) -> Self:
        self.status = NotificationStatus.DANGER
        return self

    def info(self) -> Self:
        self.status = NotificationStatus.INFO
        return self

    def seconds(self, n: int) -> Self:
        self.duration = n * 1000
        return self

    def persistent_mode(self, condition: bool = True) -> Self:
        self.persistent = condition
        return self

    def send_to_database(self) -> Self:
        self.channel = "database"
        return self

    def broadcast(self) -> Self:
        self.channel = "broadcast"
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "status": self.status.value,
            "icon": self.icon,
            "duration": self.duration,
            "persistent": self.persistent,
            "channel": self.channel,
            "actions": self.actions,
        }

    def render(self) -> str:
        body = f'<p class="or-notification-body">{e(self.body)}</p>' if self.body else ""
        return (
            f'<div class="or-notification or-notification-{e(self.status.value)}" '
            f'data-id="{e(self.id)}" role="status">'
            f'<strong class="or-notification-title">{e(self.title)}</strong>{body}</div>'
        )


class Notifier:
    """In-process notification bag (flash). Database/broadcast hooks are pluggable."""

    def __init__(self) -> None:
        self._flash: list[Notification] = []
        self._database: list[Notification] = []
        self._broadcast: list[Notification] = []

    def send(self, notification: Notification) -> Notification:
        if notification.channel == "database":
            self._database.append(notification)
        elif notification.channel == "broadcast":
            self._broadcast.append(notification)
        else:
            self._flash.append(notification)
        return notification

    def flash(self) -> list[Notification]:
        items = list(self._flash)
        self._flash.clear()
        return items

    def database(self) -> list[Notification]:
        return list(self._database)

    def broadcast_queue(self) -> list[Notification]:
        return list(self._broadcast)

    def render_flash(self) -> str:
        return '<div class="or-notifications" x-data="orbitNotifications">' + "".join(
            n.render() for n in self.flash()
        ) + "</div>"


class LiveNotifier(Notifier):
    """Broadcast / live notification host (Alpine + channel subscriptions)."""

    def __init__(self) -> None:
        super().__init__()
        self._channels: set[str] = set()

    def channel(self, name: str) -> Self:
        self._channels.add(name)
        return self

    def get_channels(self) -> list[str]:
        return sorted(self._channels)

    def render_live(self) -> str:
        channels = ",".join(self.get_channels())
        attrs = f' data-channels="{e(channels)}"' if channels else ""
        return (
            f'<div class="or-live-notifier"{attrs} x-data="orbitLiveNotifications">'
            f"{self.render_flash()}"
            f"</div>"
        )
