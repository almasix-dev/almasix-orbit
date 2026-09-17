
"""Infolist entries — read-only description list components."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon


class Entry(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._format_state: Callable[[Any], Any] | None = None
        self._url: str | Callable[..., str] | None = None
        self._copyable = False
        self._badge = False
        self._color: str | Callable[..., str] | None = None
        self._icon: str | None = None
        self._date_time = False
        self._markdown = False
        self._prose = False

    def format_state_using(self, callback: Callable[[Any], Any]) -> Self:
        self._format_state = callback
        return self

    def url(self, url: str | Callable[..., str]) -> Self:
        self._url = url
        return self

    def copyable(self, condition: bool = True) -> Self:
        self._copyable = condition
        return self

    def badge(self, condition: bool = True) -> Self:
        self._badge = condition
        return self

    def color(self, color: str | Callable[..., str]) -> Self:
        self._color = color
        return self

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def date_time(self, condition: bool = True) -> Self:
        self._date_time = condition
        return self

    def markdown(self, condition: bool = True) -> Self:
        self._markdown = condition
        return self

    def prose(self, condition: bool = True) -> Self:
        self._prose = condition
        return self

    def resolve_state(self, record: Any) -> Any:
        name = self.get_name() or ""
        if isinstance(record, dict):
            value = record.get(name)
        else:
            value = getattr(record, name, None)
        if self._format_state:
            value = self._format_state(value)
        return value

    def render(self, state: Any = None, **ctx: Any) -> str:
        record = ctx.get("record", state)
        value = self.resolve_state(record) if record is not None else state
        text = "" if value is None else str(value)
        label = e(self.get_label(record=record, state=value, **{k: v for k, v in ctx.items() if k not in ("record", "state")}))
        css = "or-badge" if self._badge else "or-entry-value"
        color = evaluate(self._color, record=record, state=value, **{k: v for k, v in ctx.items() if k not in ("record", "state")}) if self._color else None
        color_c = f" or-color-{color}" if color else ""
        ic = render_icon(self._icon) if self._icon else ""
        inner = f'<span class="{css}{color_c}">{ic}{e(text)}</span>'
        href = evaluate(self._url, record=record, state=value, **{k: v for k, v in ctx.items() if k not in ("record", "state")}) if self._url else None
        if href:
            inner = f'<a class="or-entry-link" href="{e(href)}">{inner}</a>'
        return (
            f'<div class="or-entry"><dt class="or-entry-label">{label}</dt>'
            f'<dd class="or-entry-dd">{inner}</dd></div>'
        )


class TextEntry(Entry):
    pass


class IconEntry(Entry):
    def render(self, state: Any = None, **ctx: Any) -> str:
        record = ctx.get("record", state)
        value = self.resolve_state(record) if record is not None else state
        name = str(value or self._icon or "heroicon-o-information-circle")
        label = e(self.get_label(**ctx))
        return (
            f'<div class="or-entry"><dt class="or-entry-label">{label}</dt>'
            f'<dd class="or-entry-dd">{render_icon(name)}</dd></div>'
        )


class ImageEntry(Entry):
    def render(self, state: Any = None, **ctx: Any) -> str:
        record = ctx.get("record", state)
        value = self.resolve_state(record) if record is not None else state
        label = e(self.get_label(**ctx))
        if not value:
            return f'<div class="or-entry"><dt class="or-entry-label">{label}</dt><dd></dd></div>'
        return (
            f'<div class="or-entry"><dt class="or-entry-label">{label}</dt>'
            f'<dd class="or-entry-dd"><img class="or-entry-image" src="{e(value)}" alt="" /></dd></div>'
        )


class ColorEntry(Entry):
    def render(self, state: Any = None, **ctx: Any) -> str:
        record = ctx.get("record", state)
        value = self.resolve_state(record) if record is not None else state
        label = e(self.get_label(**ctx))
        color = e(value or "#000000")
        return (
            f'<div class="or-entry"><dt class="or-entry-label">{label}</dt>'
            f'<dd class="or-entry-dd"><span class="or-color-swatch" style="background:{color}"></span> '
            f"{color}</dd></div>"
        )


class CodeEntry(Entry):
    def render(self, state: Any = None, **ctx: Any) -> str:
        record = ctx.get("record", state)
        value = self.resolve_state(record) if record is not None else state
        label = e(self.get_label(**ctx))
        return (
            f'<div class="or-entry"><dt class="or-entry-label">{label}</dt>'
            f'<dd class="or-entry-dd"><pre class="or-code"><code>{e(value)}</code></pre></dd></div>'
        )


class KeyValueEntry(Entry):
    def render(self, state: Any = None, **ctx: Any) -> str:
        record = ctx.get("record", state)
        value = self.resolve_state(record) if record is not None else state
        label = e(self.get_label(**ctx))
        rows = ""
        if isinstance(value, dict):
            rows = "".join(
                f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in value.items()
            )
        return (
            f'<div class="or-entry"><dt class="or-entry-label">{label}</dt>'
            f'<dd class="or-entry-dd"><table class="or-key-value">{rows}</table></dd></div>'
        )


class RepeatableEntry(Entry):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._schema: list[Component] = []

    def schema(self, components: list[Component]) -> Self:
        self._schema = list(components)
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        record = ctx.get("record", state)
        value = self.resolve_state(record) if record is not None else state
        label = e(self.get_label(**ctx))
        items = value if isinstance(value, (list, tuple)) else []
        blocks: list[str] = []
        for index, item in enumerate(items):
            parts: list[str] = []
            for entry in self._schema:
                if isinstance(entry, Entry):
                    parts.append(entry.render(item, record=item, index=index, **ctx))
                else:
                    parts.append(entry.render(item, record=item, index=index, **ctx))
            blocks.append(f'<div class="or-repeatable-item" data-index="{index}">{"".join(parts)}</div>')
        body = "".join(blocks) or '<p class="or-empty">No items</p>'
        return (
            f'<div class="or-entry or-entry-repeatable"><dt class="or-entry-label">{label}</dt>'
            f'<dd class="or-entry-dd"><div class="or-repeatable">{body}</div></dd></div>'
        )
