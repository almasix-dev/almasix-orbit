"""Fluent SDUI component base (Filament-style ``make`` + chained configurators)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self, TypeVar

T = TypeVar("T", bound="Component")


class Component:
    """Base configuration object for Orbit schemas, fields, columns, and entries."""

    def __init__(self, name: str | None = None) -> None:
        self._name = name
        self._label: str | None = None
        self._hidden = False
        self._visible: bool | Callable[..., bool] = True
        self._disabled: bool | Callable[..., bool] = False
        self._extra_attributes: dict[str, Any] = {}
        self._view: str | None = None
        self._column_span: int | str | None = None
        self._live = False
        self._dehydrated = True
        self._state_path: str | None = None
        self._default: Any = None
        self._helper_text: str | None = None
        self._hint: str | None = None
        self._hint_icon: str | None = None

    @classmethod
    def make(cls, name: str | None = None) -> Self:
        return cls(name)

    def get_name(self) -> str | None:
        return self._name

    def label(self, label: str | None) -> Self:
        self._label = label
        return self

    def get_label(self) -> str:
        if self._label is not None:
            return self._label
        if not self._name:
            return ""
        return self._name.replace("_", " ").replace(".", " ").title()

    def hidden(self, condition: bool = True) -> Self:
        self._hidden = condition
        return self

    def visible(self, condition: bool | Callable[..., bool] = True) -> Self:
        self._visible = condition
        return self

    def disabled(self, condition: bool | Callable[..., bool] = True) -> Self:
        self._disabled = condition
        return self

    def is_hidden(self) -> bool:
        return self._hidden

    def is_visible(self, **ctx: Any) -> bool:
        if self._hidden:
            return False
        v = self._visible
        return bool(v(**ctx) if callable(v) else v)

    def is_disabled(self, **ctx: Any) -> bool:
        d = self._disabled
        return bool(d(**ctx) if callable(d) else d)

    def extra_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_attributes.update(attrs)
        return self

    def get_extra_attributes(self) -> dict[str, Any]:
        return dict(self._extra_attributes)

    def view(self, view: str) -> Self:
        self._view = view
        return self

    def get_view(self) -> str | None:
        return self._view

    def column_span(self, span: int | str) -> Self:
        self._column_span = span
        return self

    def live(self, condition: bool = True) -> Self:
        self._live = condition
        return self

    def dehydrated(self, condition: bool = True) -> Self:
        self._dehydrated = condition
        return self

    def is_dehydrated(self) -> bool:
        return self._dehydrated

    def state_path(self, path: str) -> Self:
        self._state_path = path
        return self

    def get_state_path(self) -> str | None:
        return self._state_path or self._name

    def default(self, value: Any) -> Self:
        self._default = value
        return self

    def get_default(self) -> Any:
        return self._default

    def helper_text(self, text: str) -> Self:
        self._helper_text = text
        return self

    def hint(self, text: str) -> Self:
        self._hint = text
        return self

    def hint_icon(self, icon_name: str) -> Self:
        self._hint_icon = icon_name
        return self

    def configure(self, callback: Callable[[Self], Any]) -> Self:
        callback(self)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": type(self).__name__,
            "name": self._name,
            "label": self.get_label(),
            "hidden": self._hidden,
            "live": self._live,
            "dehydrated": self._dehydrated,
            "state_path": self.get_state_path(),
            "default": self._default,
            "helper_text": self._helper_text,
            "hint": self._hint,
            "column_span": self._column_span,
            "extra_attributes": self._extra_attributes,
        }

    def render(self, state: Any = None, **ctx: Any) -> str:
        """Default HTML render — subclasses override for richer markup."""
        from almasix.orbit.support.html import e

        if not self.is_visible(**ctx):
            return ""
        label = e(self.get_label())
        name = e(self.get_state_path() or "")
        value = "" if state is None else e(str(state))
        disabled = " disabled" if self.is_disabled(**ctx) else ""
        return (
            f'<div class="or-field" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<input class="or-input" id="or-{name}" name="{name}" '
            f'value="{value}"{disabled} />'
            f"</div>"
        )


def schema_components(components: Sequence[Component]) -> list[dict[str, Any]]:
    return [c.to_dict() for c in components]
