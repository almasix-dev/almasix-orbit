"""Fluent SDUI component base (Filament-style ``make`` + chained configurators)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self, TypeVar

from almasix.orbit.support.evaluate import evaluate

T = TypeVar("T", bound="Component")


class Component:
    """Base configuration object for Orbit schemas, fields, columns, and entries."""

    def __init__(self, name: str | None = None) -> None:
        self._name = name
        self._label: str | Callable[..., str] | None = None
        self._hidden = False
        self._visible: bool | Callable[..., bool] = True
        self._disabled: bool | Callable[..., bool] = False
        self._extra_attributes: dict[str, Any] = {}
        self._view: str | None = None
        self._column_span: int | str | None = None
        self._live = False
        self._live_on_blur = False
        self._live_debounce: int | None = None
        self._dehydrated = True
        self._state_path: str | None = None
        self._default: Any = None
        self._helper_text: str | Callable[..., str] | None = None
        self._hint: str | Callable[..., str] | None = None
        self._hint_icon: str | Callable[..., str] | None = None
        self._hidden_label = False
        self._inline_label = False

    @classmethod
    def make(cls, name: str | None = None) -> Self:
        # Avoid passing explicit None so subclass __init__ defaults (e.g. "view") apply.
        return cls() if name is None else cls(name)

    def get_name(self) -> str | None:
        return self._name

    def label(self, label: str | Callable[..., str] | None) -> Self:
        self._label = label
        return self

    def get_label(self, **ctx: Any) -> str:
        if self._label is not None:
            result = evaluate(self._label, **ctx)
            return "" if result is None else str(result)
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
        return bool(evaluate(self._visible, **ctx))

    def is_disabled(self, **ctx: Any) -> bool:
        return bool(evaluate(self._disabled, **ctx))

    def extra_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_attributes.update(attrs)
        return self

    def get_extra_attributes(self, **ctx: Any) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in self._extra_attributes.items():
            out[key] = evaluate(value, **ctx)
        return out

    def view(self, view: str) -> Self:
        self._view = view
        return self

    def get_view(self) -> str | None:
        return self._view

    def column_span(self, span: int | str) -> Self:
        self._column_span = span
        return self

    def live(
        self,
        condition: bool = True,
        *,
        on_blur: bool = False,
        debounce: int | None = None,
    ) -> Self:
        self._live = condition
        self._live_on_blur = on_blur
        self._live_debounce = debounce
        return self

    def wire_model_directive(self) -> str:
        """Return the model binding key (``model``, ``model.live``, …) without prefix."""
        if self._live_on_blur:
            return "model.blur"
        if self._live and self._live_debounce is not None:
            return f"model.live.debounce.{int(self._live_debounce)}ms"
        if self._live:
            return "model.live"
        return "model"

    def wire_model_attrs(self, name: str) -> str:
        """Dual ``conduit:model*`` / ``wire:model*`` attributes for ``name``."""
        from almasix.orbit.support.conduit_attrs import conduit_attr

        return conduit_attr(self.wire_model_directive(), name)

    def dehydrated(self, condition: bool = True) -> Self:
        self._dehydrated = condition
        return self

    def saved(self, condition: bool = True) -> Self:
        """Filament 5 alias for ``dehydrated``."""
        return self.dehydrated(condition)

    def hidden_label(self, condition: bool = True) -> Self:
        self._hidden_label = condition
        return self

    def inline_label(self, condition: bool = True) -> Self:
        self._inline_label = condition
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

    def get_default(self, **ctx: Any) -> Any:
        return evaluate(self._default, **ctx)

    def helper_text(self, text: str | Callable[..., str]) -> Self:
        self._helper_text = text
        return self

    def get_helper_text(self, **ctx: Any) -> str | None:
        if self._helper_text is None:
            return None
        result = evaluate(self._helper_text, **ctx)
        return None if result is None else str(result)

    def hint(self, text: str | Callable[..., str]) -> Self:
        self._hint = text
        return self

    def get_hint(self, **ctx: Any) -> str | None:
        if self._hint is None:
            return None
        result = evaluate(self._hint, **ctx)
        return None if result is None else str(result)

    def hint_icon(self, icon_name: str | Callable[..., str]) -> Self:
        self._hint_icon = icon_name
        return self

    def get_hint_icon(self, **ctx: Any) -> str | None:
        if self._hint_icon is None:
            return None
        result = evaluate(self._hint_icon, **ctx)
        return None if result is None else str(result)

    def configure(self, callback: Callable[[Self], Any]) -> Self:
        callback(self)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": type(self).__name__,
            "name": self._name,
            "label": self.get_label() if not callable(self._label) else None,
            "hidden": self._hidden,
            "live": self._live,
            "dehydrated": self._dehydrated,
            "state_path": self.get_state_path(),
            "default": self._default if not callable(self._default) else None,
            "helper_text": self._helper_text if not callable(self._helper_text) else None,
            "hint": self._hint if not callable(self._hint) else None,
            "column_span": self._column_span,
            "extra_attributes": {
                k: v for k, v in self._extra_attributes.items() if not callable(v)
            },
        }

    def render(self, state: Any = None, **ctx: Any) -> str:
        """Default HTML render — subclasses override for richer markup."""
        from almasix.orbit.support.html import e

        if not self.is_visible(**ctx):
            return ""
        label = e(self.get_label(**ctx))
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
