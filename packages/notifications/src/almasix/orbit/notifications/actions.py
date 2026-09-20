"""Actions rendered inside a notification toast / database row."""

from __future__ import annotations

from typing import Any, Self

from almasix.orbit.support.html import e


class NotificationAction:
    """Fluent action for notification footers (Filament ``NotificationAction`` parity)."""

    def __init__(self, name: str = "action") -> None:
        self._name = name
        self._label: str | None = None
        self._button = False
        self._url: str | None = None
        self._open_url_in_new_tab = False
        self._dispatch_event: str | None = None
        self._dispatch_payload: list[Any] = []
        self._dispatch_self = False
        self._dispatch_to: str | None = None
        self._close = False
        self._color: str | None = None
        self._mark_as_read = False
        self._mark_as_unread = False

    @classmethod
    def make(cls, name: str = "action") -> Self:
        return cls(name)

    def label(self, value: str) -> Self:
        self._label = value
        return self

    def button(self, condition: bool = True) -> Self:
        self._button = bool(condition)
        return self

    def url(self, value: str, *, should_open_in_new_tab: bool = False) -> Self:
        self._url = value
        if should_open_in_new_tab:
            self._open_url_in_new_tab = True
        return self

    def open_url_in_new_tab(self, condition: bool = True) -> Self:
        self._open_url_in_new_tab = bool(condition)
        return self

    def dispatch(self, event: str, payload: list[Any] | None = None) -> Self:
        self._dispatch_event = event
        self._dispatch_payload = list(payload or [])
        self._dispatch_self = False
        self._dispatch_to = None
        return self

    def dispatch_self(self, event: str, payload: list[Any] | None = None) -> Self:
        self.dispatch(event, payload)
        self._dispatch_self = True
        return self

    def dispatch_to(
        self,
        component: str,
        event: str,
        payload: list[Any] | None = None,
    ) -> Self:
        self.dispatch(event, payload)
        self._dispatch_to = component
        return self

    def close(self, condition: bool = True) -> Self:
        self._close = bool(condition)
        return self

    def color(self, value: str) -> Self:
        self._color = value
        return self

    def mark_as_read(self, condition: bool = True) -> Self:
        self._mark_as_read = bool(condition)
        return self

    def mark_as_unread(self, condition: bool = True) -> Self:
        self._mark_as_unread = bool(condition)
        return self

    def get_name(self) -> str:
        return self._name

    def get_label(self) -> str:
        return self._label or self._name.replace("_", " ").replace("-", " ").title()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "label": self.get_label(),
            "button": self._button,
            "url": self._url,
            "open_url_in_new_tab": self._open_url_in_new_tab,
            "dispatch": self._dispatch_event,
            "dispatch_payload": list(self._dispatch_payload),
            "dispatch_self": self._dispatch_self,
            "dispatch_to": self._dispatch_to,
            "close": self._close,
            "color": self._color,
            "mark_as_read": self._mark_as_read,
            "mark_as_unread": self._mark_as_unread,
        }

    def render(self) -> str:
        label = e(self.get_label())
        classes = ["or-notification-action"]
        if self._button:
            classes.append("or-btn")
            classes.append("or-btn-sm")
        if self._color:
            classes.append(f"or-notification-action-{e(self._color)}")
        class_attr = " ".join(classes)
        attrs = [
            f'class="{class_attr}"',
            f'data-action-name="{e(self._name)}"',
            'type="button"',
        ]
        if self._url:
            tag = "a"
            attrs = [
                f'class="{class_attr}"',
                f'href="{e(self._url)}"',
                f'data-action-name="{e(self._name)}"',
            ]
            if self._open_url_in_new_tab:
                attrs.extend(['target="_blank"', 'rel="noopener noreferrer"'])
        else:
            tag = "button"
        if self._dispatch_event:
            attrs.append(f'data-dispatch="{e(self._dispatch_event)}"')
        if self._close:
            attrs.append('data-close="true"')
        if self._mark_as_read:
            attrs.append('data-mark-as-read="true"')
        if self._mark_as_unread:
            attrs.append('data-mark-as-unread="true"')
        return f"<{tag} {' '.join(attrs)}>{label}</{tag}>"
