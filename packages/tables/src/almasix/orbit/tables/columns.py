
"""Table columns."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, datetime
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
        self._summarizers: list[Any] = []
        self._money_currency: str | None = None
        self._money_divide_by: float | int = 1
        self._date_format: str | None = None
        self._description: str | Callable[..., str] | None = None

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

    def summarize(self, summarizers: Any | Sequence[Any]) -> Self:
        from almasix.orbit.tables.summaries import Summarizer

        if isinstance(summarizers, Summarizer):
            self._summarizers = [summarizers]
        else:
            self._summarizers = list(summarizers)
        return self

    def get_summarizers(self) -> list[Any]:
        return list(self._summarizers)

    def money(
        self,
        currency: str = "USD",
        *,
        divide_by: float | int = 1,
    ) -> Self:
        self._money_currency = currency
        self._money_divide_by = divide_by
        return self

    def date(self, format: str = "%Y-%m-%d") -> Self:
        self._date_format = format
        return self

    def description(self, text: str | Callable[..., str]) -> Self:
        self._description = text
        return self

    def get_description(self, **ctx: Any) -> str | None:
        if self._description is None:
            return None
        from almasix.orbit.support.evaluate import evaluate

        result = evaluate(self._description, **ctx)
        return None if result is None else str(result)

    def _format_display_value(self, value: Any) -> str:
        if value is None:
            return ""
        if self._money_currency is not None:
            try:
                num = float(value) / float(self._money_divide_by)
            except (TypeError, ValueError):
                return str(value)
            return f"{self._money_currency} {num:.2f}"
        if self._date_format is not None:
            if isinstance(value, datetime):
                return value.strftime(self._date_format)
            if isinstance(value, date):
                return value.strftime(self._date_format)
            text = str(value)
            try:
                if "T" in text:
                    return datetime.fromisoformat(text[:19]).strftime(self._date_format)
                return datetime.strptime(text[:10], "%Y-%m-%d").strftime(self._date_format)
            except ValueError:
                return text
        return str(value)

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
        elif self._money_currency is not None or self._date_format is not None:
            text = self._format_display_value(value)
        else:
            text = "" if value is None else str(value)
        css = "or-badge" if self._badge else "or-cell-text"
        color = self._color
        if callable(color):
            from almasix.orbit.support.evaluate import evaluate

            color = evaluate(color, record=record, state=value, **ctx)
        color_c = f" or-color-{color}" if color else ""
        desc = self.get_description(record=record, state=value, **ctx)
        desc_attr = f' title="{e(desc)}" data-description="{e(desc)}"' if desc else ""
        inner = f'<span class="{css}{color_c}"{desc_attr}>{e(text)}</span>'
        href = None
        if self._url is not None:
            from almasix.orbit.support.evaluate import evaluate

            href = evaluate(self._url, record=record, state=value, **ctx)
        if href:
            inner = f'<a class="or-cell-link" href="{e(href)}">{inner}</a>'
        return f'<td class="or-td">{inner}</td>'

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "sortable": self._sortable,
                "searchable": self._searchable,
                "badge": self._badge,
                "has_summarizers": bool(self._summarizers),
                "money_currency": self._money_currency,
                "date_format": self._date_format,
            }
        )
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
