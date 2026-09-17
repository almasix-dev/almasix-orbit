
"""Table columns."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e


class Column(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._sortable = False
        self._searchable = False
        self._toggleable = True
        self._format_state: Callable[[Any], Any] | None = None
        self._badge = False
        self._boolean = False
        self._color: str | Callable[..., str] | None = None
        self._limit: int | None = None
        self._wrap = False
        self._url: str | Callable[..., str] | None = None
        self._weight: str | None = None
        self._copyable = False

    def sortable(self, condition: bool = True) -> Self:
        self._sortable = condition
        return self

    def searchable(self, condition: bool = True) -> Self:
        self._searchable = condition
        return self

    def toggleable(self, condition: bool = True) -> Self:
        self._toggleable = condition
        return self

    def format_state_using(self, callback: Callable[[Any], Any]) -> Self:
        self._format_state = callback
        return self

    def badge(self, condition: bool = True) -> Self:
        self._badge = condition
        return self

    def boolean(self, condition: bool = True) -> Self:
        self._boolean = condition
        return self

    def color(self, color: str | Callable[..., str]) -> Self:
        self._color = color
        return self

    def limit(self, length: int) -> Self:
        self._limit = length
        return self

    def wrap(self, condition: bool = True) -> Self:
        self._wrap = condition
        return self

    def url(self, url: str | Callable[..., str]) -> Self:
        self._url = url
        return self

    def weight(self, weight: str) -> Self:
        self._weight = weight
        return self

    def copyable(self, condition: bool = True) -> Self:
        self._copyable = condition
        return self

    def is_sortable(self) -> bool:
        return self._sortable

    def is_searchable(self) -> bool:
        return self._searchable

    def resolve_state(self, record: Any) -> Any:
        name = self.get_name() or ""
        if isinstance(record, dict):
            value = record.get(name)
        else:
            value = getattr(record, name, None)
        if self._format_state:
            value = self._format_state(value)
        if self._limit is not None and isinstance(value, str) and len(value) > self._limit:
            value = value[: self._limit] + "…"
        return value

    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record)
        if self._boolean:
            text = "Yes" if value else "No"
        else:
            text = "" if value is None else str(value)
        css = "or-badge" if self._badge else "or-cell-text"
        color = self._color
        if callable(color):
            from almasix.orbit.support.evaluate import evaluate

            color = evaluate(color, record=record, state=value, **ctx)
        color_c = f" or-color-{color}" if color else ""
        inner = f'<span class="{css}{color_c}">{e(text)}</span>'
        href = None
        if self._url is not None:
            from almasix.orbit.support.evaluate import evaluate

            href = evaluate(self._url, record=record, state=value, **ctx)
        if href:
            inner = f'<a class="or-cell-link" href="{e(href)}">{inner}</a>'
        return f'<td class="or-td">{inner}</td>'

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update({"sortable": self._sortable, "searchable": self._searchable, "badge": self._badge})
        return d


class TextColumn(Column):
    pass


class BadgeColumn(Column):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._badge = True


class BooleanColumn(Column):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._boolean = True


class IconColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        from almasix.orbit.support.icons import icon as render_icon

        value = self.resolve_state(record)
        name = str(value or "heroicon-o-check")
        return f'<td class="or-td">{render_icon(name)}</td>'


class ImageColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record)
        if not value:
            return '<td class="or-td"></td>'
        return f'<td class="or-td"><img class="or-avatar" src="{e(value)}" alt="" /></td>'


class ColorColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record) or "#000000"
        return (
            f'<td class="or-td"><span class="or-color-swatch" style="background:{e(value)}" '
            f'title="{e(value)}"></span></td>'
        )


class SelectColumn(Column):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._options: dict[Any, Any] | Callable[..., dict[Any, Any]] = {}

    def options(self, options: dict[Any, Any] | Callable[..., dict[Any, Any]]) -> Self:
        self._options = options
        return self

    def render_cell(self, record: Any, **ctx: Any) -> str:
        from almasix.orbit.support.evaluate import evaluate

        value = self.resolve_state(record)
        name = e(self.get_name() or "")
        opts = evaluate(self._options, record=record, state=value, **ctx)
        if not isinstance(opts, dict):
            opts = {}
        options_html = []
        for k, v in opts.items():
            sel = " selected" if str(k) == str(value) else ""
            options_html.append(f'<option value="{e(k)}"{sel}>{e(v)}</option>')
        return (
            f'<td class="or-td"><select class="or-select or-select-inline" name="{name}" '
            f'wire:model="table.{name}">{"".join(options_html)}</select></td>'
        )


class TagsColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record) or []
        if isinstance(value, str):
            value = [v.strip() for v in value.split(",") if v.strip()]
        badges = "".join(f'<span class="or-badge">{e(v)}</span>' for v in value)
        return f'<td class="or-td">{badges}</td>'


class CheckboxColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record)
        name = e(self.get_name() or "")
        checked = " checked" if value else ""
        return (
            f'<td class="or-td"><input type="checkbox" class="or-checkbox" name="{name}"'
            f'{checked} wire:model="table.{name}" /></td>'
        )


class TextInputColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record)
        name = e(self.get_name() or "")
        val = "" if value is None else e(str(value))
        return (
            f'<td class="or-td"><input class="or-input or-input-inline" name="{name}" '
            f'value="{val}" wire:model.blur="table.{name}" /></td>'
        )


class ToggleColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record)
        name = e(self.get_name() or "")
        checked = " checked" if value else ""
        return (
            f'<td class="or-td"><input type="checkbox" class="or-toggle" name="{name}"'
            f'{checked} wire:model.live="table.{name}" /></td>'
        )


class ViewColumn(Column):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._view_html: Callable[..., str] | str | None = None

    def content(self, html: Callable[..., str] | str) -> Self:
        self._view_html = html
        return self

    def render_cell(self, record: Any, **ctx: Any) -> str:
        from almasix.orbit.support.evaluate import evaluate

        value = self.resolve_state(record)
        if self._view_html is not None:
            body = evaluate(self._view_html, record=record, state=value, **ctx)
        else:
            body = e("" if value is None else str(value))
        return f'<td class="or-td"><div class="or-view-column">{body}</div></td>'


class ColumnGroup(Component):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._columns: list[Column] = []

    def columns(self, cols: list[Column]) -> Self:
        self._columns = list(cols)
        return self

    def get_columns(self) -> list[Column]:
        return list(self._columns)
