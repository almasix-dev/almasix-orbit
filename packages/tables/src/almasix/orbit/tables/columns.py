"""Table columns."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, datetime
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e


def _record_id(record: Any) -> str:
    if isinstance(record, dict):
        rid = record.get("id")
    else:
        rid = getattr(record, "id", None)
    if rid is None:
        rid = id(record)
    return str(rid)


def _simple_markdown(text: str) -> str:
    """Tiny safe markdown subset: escape, then **bold**, *italic*, newlines."""
    out = e(text)
    # Bold then italic (order matters for nested-ish cases)
    import re

    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", out)
    out = out.replace("\n", "<br />")
    return out


def _copyable_wrap(inner: str, copy_text: str) -> str:
    return (
        f'<span class="or-copyable" data-copy="{e(copy_text)}" title="Copy">'
        f"{inner}"
        f'<button type="button" class="or-copy-btn" aria-label="Copy" '
        f'@click.stop="navigator.clipboard.writeText($el.closest(\'[data-copy]\').dataset.copy)">'
        f'<span class="or-copy-glyph" aria-hidden="true">⎘</span></button></span>'
    )


def dot_get(record: Any, path: str) -> Any:
    """Resolve ``author.name`` / nested dict keys on a record."""
    current: Any = record
    for part in str(path).split("."):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
    return current


def _attrs_to_html(attrs: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, value in attrs.items():
        if value is True:
            parts.append(e(str(key)))
        elif value is False or value is None:
            continue
        else:
            parts.append(f'{e(str(key))}="{e(value)}"')
    return (" " + " ".join(parts)) if parts else ""


class Column(Component):
    _configure_using: list[Callable[[Column], None]] = []

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._sortable = False
        self._searchable = False
        self._sort_columns: list[str] | None = None
        self._sort_query: Callable[..., Any] | None = None
        self._search_columns: list[str] | None = None
        self._search_query: Callable[..., Any] | None = None
        self._state: Any = None
        self._has_custom_state = False
        self._placeholder: str | Callable[..., str] | None = None
        self._tooltip: str | Callable[..., str] | None = None
        self._header_tooltip: str | Callable[..., str] | None = None
        self._wrap_header = False
        self._width: str | int | None = None
        self._grow = False
        self._vertical_alignment: str = "start"
        self._open_url_in_new_tab = False
        self._extra_cell_attributes: dict[str, Any] = {}
        self._extra_header_attributes: dict[str, Any] = {}
        self._toggleable = True
        self._toggled_hidden_by_default = False
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
        self._numeric: bool = False
        self._numeric_decimal_places: int | None = None
        self._description: str | Callable[..., str] | None = None
        self._visible_from: str | None = None
        self._hidden_from: str | None = None
        self._list_bullet = False
        self._markdown = False
        self._html = False
        self._alignment: str = "start"
        self._icon: str | Callable[..., str] | None = None

    @classmethod
    def configure_using(cls, callback: Callable[[Column], None]) -> None:
        """Register a default configurator (Filament ``Column::configureUsing``)."""
        cls._configure_using.append(callback)

    @classmethod
    def make(cls, name: str | None = None) -> Self:
        instance = cls() if name is None else cls(name)
        for callback in cls._configure_using:
            callback(instance)
        return instance

    def alignment(self, value: str) -> Self:
        """Cell/header alignment: ``start``, ``center``, or ``end`` (Filament parity)."""
        self._alignment = value
        return self

    def align_start(self) -> Self:
        return self.alignment("start")

    def align_center(self) -> Self:
        return self.alignment("center")

    def align_end(self) -> Self:
        return self.alignment("end")

    def get_alignment(self) -> str:
        return self._alignment or "start"

    def vertically_align(self, value: str) -> Self:
        """Vertical alignment: ``start``, ``center``, or ``end``."""
        self._vertical_alignment = value
        return self

    def vertically_align_start(self) -> Self:
        return self.vertically_align("start")

    def vertically_align_center(self) -> Self:
        return self.vertically_align("center")

    def vertically_align_end(self) -> Self:
        return self.vertically_align("end")

    def get_vertical_alignment(self) -> str:
        return self._vertical_alignment or "start"

    def state(self, value: Any) -> Self:
        """Override cell state (static or callable)."""
        self._state = value
        self._has_custom_state = True
        return self

    def placeholder(self, text: str | Callable[..., str]) -> Self:
        """Display text when state is empty (not treated as real state)."""
        self._placeholder = text
        return self

    def tooltip(self, text: str | Callable[..., str]) -> Self:
        self._tooltip = text
        return self

    def header_tooltip(self, text: str | Callable[..., str]) -> Self:
        self._header_tooltip = text
        return self

    def wrap_header(self, condition: bool = True) -> Self:
        self._wrap_header = condition
        return self

    def width(self, value: str | int) -> Self:
        self._width = value
        return self

    def grow(self, condition: bool = True) -> Self:
        self._grow = condition
        return self

    def open_url_in_new_tab(self, condition: bool = True) -> Self:
        self._open_url_in_new_tab = condition
        return self

    def extra_cell_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_cell_attributes.update(attrs)
        return self

    def extra_header_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_header_attributes.update(attrs)
        return self

    def sortable(
        self,
        condition: bool | Sequence[str] = True,
        *,
        query: Callable[..., Any] | None = None,
    ) -> Self:
        """Enable sorting. Pass attribute keys or ``query(records, direction)``."""
        if query is not None:
            self._sortable = True
            self._sort_query = query
            self._sort_columns = None
            return self
        if isinstance(condition, (list, tuple)):
            self._sortable = True
            self._sort_columns = [str(c) for c in condition]
            self._sort_query = None
            return self
        self._sortable = bool(condition)
        if not self._sortable:
            self._sort_columns = None
            self._sort_query = None
        return self

    def searchable(
        self,
        condition: bool | Sequence[str] = True,
        *,
        query: Callable[..., Any] | None = None,
    ) -> Self:
        """Enable search. Pass attribute keys or ``query(record, search) -> bool``."""
        if query is not None:
            self._searchable = True
            self._search_query = query
            self._search_columns = None
            return self
        if isinstance(condition, (list, tuple)):
            self._searchable = True
            self._search_columns = [str(c) for c in condition]
            self._search_query = None
            return self
        self._searchable = bool(condition)
        if not self._searchable:
            self._search_columns = None
            self._search_query = None
        return self

    def toggleable(
        self,
        condition: bool = True,
        *,
        is_toggled_hidden_by_default: bool = False,
    ) -> Self:
        self._toggleable = condition
        if condition:
            self._toggled_hidden_by_default = is_toggled_hidden_by_default
        return self

    def is_toggleable(self) -> bool:
        return bool(self._toggleable)

    def is_toggled_hidden_by_default(self) -> bool:
        return bool(self._toggled_hidden_by_default)

    def format_state_using(self, callback: Callable[[Any], Any]) -> Self:
        self._format_state = callback
        return self

    def get_sort_key(self, record: Any) -> Any:
        """Value(s) used when sorting this column (without a custom query)."""
        if self._sort_columns:
            return tuple(
                "" if (v := dot_get(record, key)) is None else v
                for key in self._sort_columns
            )
        value = self.resolve_state(record)
        return "" if value is None else value

    def matches_search(self, record: Any, term: str) -> bool:
        """Whether this column matches ``term`` (already lowercased)."""
        from almasix.orbit.support.evaluate import evaluate

        if self._search_query is not None:
            result = evaluate(self._search_query, record=record, search=term)
            if isinstance(result, bool):
                return result
            try:
                return bool(self._search_query(record, term))
            except TypeError:
                return bool(result)
        keys = self._search_columns
        if keys:
            for key in keys:
                val = dot_get(record, key)
                if val is not None and term in str(val).lower():
                    return True
            return False
        val = self.resolve_state(record)
        return val is not None and term in str(val).lower()

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

    def icon(self, name: str | Callable[..., str]) -> Self:
        self._icon = name
        return self

    def summarize(self, *summarizers: Any) -> Self:
        from almasix.orbit.tables.summaries import Summarizer

        items: list[Any] = []
        for item in summarizers:
            if isinstance(item, Summarizer):
                items.append(item)
            elif isinstance(item, (list, tuple)):
                items.extend(item)
            else:
                items.append(item)
        self._summarizers = items
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

    def date_time(self, format: str = "%Y-%m-%d %H:%M") -> Self:
        return self.date(format)

    def numeric(self, decimal_places: int | None = None) -> Self:
        self._numeric = True
        self._numeric_decimal_places = decimal_places
        return self

    def list_with_line_breaks(self, condition: bool = True) -> Self:
        self._list_bullet = condition
        return self

    def markdown(self, condition: bool = True) -> Self:
        self._markdown = condition
        return self

    def html(self, condition: bool = True) -> Self:
        self._html = condition
        return self

    def visible_from(self, breakpoint: str) -> Self:
        self._visible_from = breakpoint
        return self

    def hidden_from(self, breakpoint: str) -> Self:
        self._hidden_from = breakpoint
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
        if self._list_bullet and isinstance(value, (list, tuple)):
            return "\n".join(f"• {item}" for item in value)
        if self._money_currency is not None:
            try:
                num = float(value) / float(self._money_divide_by)
            except (TypeError, ValueError):
                return str(value)
            return f"{self._money_currency} {num:.2f}"
        if self._numeric:
            try:
                num = float(value)
            except (TypeError, ValueError):
                return str(value)
            if self._numeric_decimal_places is not None:
                return f"{num:.{self._numeric_decimal_places}f}"
            if num == int(num):
                return str(int(num))
            return str(num)
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
        return bool(self._sortable)

    def is_searchable(self) -> bool:
        return bool(self._searchable)

    def resolve_state(self, record: Any, **ctx: Any) -> Any:
        from almasix.orbit.support.evaluate import evaluate

        if self._has_custom_state:
            value = evaluate(self._state, record=record, **ctx)
        else:
            name = self.get_name() or ""
            value = dot_get(record, name) if name else None
        if value is None and self._default is not None:
            value = self.get_default(record=record, **ctx)
        if self._format_state:
            value = self._format_state(value)
        if self._limit is not None and isinstance(value, str) and len(value) > self._limit:
            value = value[: self._limit] + "…"
        return value

    def _resolved_placeholder(self, record: Any, **ctx: Any) -> str | None:
        if self._placeholder is None:
            return None
        from almasix.orbit.support.evaluate import evaluate

        result = evaluate(self._placeholder, record=record, **ctx)
        return None if result is None else str(result)

    def _resolved_tooltip(self, record: Any, value: Any, **ctx: Any) -> str | None:
        if self._tooltip is None:
            return None
        from almasix.orbit.support.evaluate import evaluate

        result = evaluate(self._tooltip, record=record, state=value, **ctx)
        return None if result is None else str(result)

    def get_header_tooltip(self, **ctx: Any) -> str | None:
        if self._header_tooltip is None:
            return None
        from almasix.orbit.support.evaluate import evaluate

        result = evaluate(self._header_tooltip, **ctx)
        return None if result is None else str(result)

    def _width_style(self) -> str:
        if self._width is None:
            return ""
        if isinstance(self._width, int) or str(self._width).isdigit():
            return f"width:{int(self._width)}px"
        return f"width:{self._width}"

    def _td_classes(self, extra: str = "") -> str:
        classes = ["or-td"]
        if self._visible_from:
            classes.append(f"or-visible-from-{self._visible_from}")
        if self._hidden_from:
            classes.append(f"or-hidden-from-{self._hidden_from}")
        align = self.get_alignment()
        if align and align != "start":
            classes.append(f"or-align-{align}")
        valign = self.get_vertical_alignment()
        if valign and valign != "start":
            classes.append(f"or-v-align-{valign}")
        if self._grow:
            classes.append("or-col-grow")
        if extra:
            classes.append(extra.strip())
        return " ".join(classes)

    def _td_open_tag(self, record: Any, value: Any, **ctx: Any) -> str:
        from almasix.orbit.support.evaluate import evaluate

        attrs = {
            **self.get_extra_attributes(record=record, state=value, **ctx),
            **{
                k: evaluate(v, record=record, state=value, **ctx)
                for k, v in self._extra_cell_attributes.items()
            },
        }
        style_parts: list[str] = []
        width = self._width_style()
        if width:
            style_parts.append(width)
        if "style" in attrs and attrs["style"]:
            style_parts.append(str(attrs.pop("style")))
        if style_parts:
            attrs["style"] = ";".join(style_parts)
        return f'<td class="{self._td_classes()}"{_attrs_to_html(attrs)}>'

    def _resolve_color(self, record: Any, value: Any, **ctx: Any) -> str | None:
        color = self._color
        if callable(color):
            from almasix.orbit.support.evaluate import evaluate

            color = evaluate(color, record=record, state=value, **ctx)
        return str(color) if color else None

    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record, **ctx)
        using_placeholder = False
        if value is None or value == "":
            placeholder = self._resolved_placeholder(record, state=value, **ctx)
            if placeholder is not None:
                text = placeholder
                using_placeholder = True
            elif self._boolean:
                text = "No"
            else:
                text = ""
        elif self._boolean:
            text = "Yes" if value else "No"
        elif (
            self._money_currency is not None
            or self._date_format is not None
            or self._numeric
            or self._list_bullet
        ):
            text = self._format_display_value(value)
        else:
            text = str(value)
        css = "or-badge" if self._badge else "or-cell-text"
        if using_placeholder:
            css += " or-cell-placeholder"
        color = None if using_placeholder else self._resolve_color(record, value, **ctx)
        color_c = f" or-color-{color}" if color else ""
        weight_c = f" or-font-{e(self._weight)}" if self._weight else ""
        wrap_c = " or-cell-wrap" if self._wrap else ""
        desc = self.get_description(record=record, state=value, **ctx)
        tip = self._resolved_tooltip(record, value, **ctx)
        title_parts = [p for p in (tip, desc) if p]
        title_attr = f' title="{e(title_parts[0])}"' if title_parts else ""
        desc_attr = f' data-description="{e(desc)}"' if desc else ""
        desc_html = (
            f'<span class="or-cell-description">{e(desc)}</span>' if desc else ""
        )
        if using_placeholder:
            body = e(text)
        elif self._html:
            body = str(text)
        elif self._markdown:
            body = _simple_markdown(text)
        else:
            body = e(text).replace("\n", "<br />") if self._list_bullet else e(text)
        icon_html = ""
        if self._icon is not None and not using_placeholder:
            from almasix.orbit.support.evaluate import evaluate
            from almasix.orbit.support.icons import icon as render_icon

            icon_name = evaluate(self._icon, record=record, state=value, **ctx)
            if icon_name:
                icon_html = f'<span class="or-cell-icon">{render_icon(str(icon_name))}</span>'
        inner = (
            f'<span class="{css}{color_c}{weight_c}{wrap_c}"{title_attr}{desc_attr}>'
            f"{icon_html}{body}{desc_html}</span>"
        )
        if self._copyable and text and not using_placeholder:
            inner = _copyable_wrap(inner, text)
        href = None
        if self._url is not None and not using_placeholder:
            from almasix.orbit.support.evaluate import evaluate

            href = evaluate(self._url, record=record, state=value, **ctx)
        if href:
            target = ' target="_blank" rel="noopener noreferrer"' if self._open_url_in_new_tab else ""
            inner = f'<a class="or-cell-link" href="{e(href)}"{target}>{inner}</a>'
        return f"{self._td_open_tag(record, value, **ctx)}{inner}</td>"

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "sortable": self._sortable,
                "searchable": self._searchable,
                "toggleable": self._toggleable,
                "toggled_hidden_by_default": self._toggled_hidden_by_default,
                "badge": self._badge,
                "has_summarizers": bool(self._summarizers),
                "money_currency": self._money_currency,
                "date_format": self._date_format,
                "alignment": self._alignment,
                "wrap_header": self._wrap_header,
                "grow": self._grow,
                "width": self._width,
            }
        )
        return d


class TextColumn(Column):
    pass


class BadgeColumn(Column):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._badge = True


class IconColumn(Column):
    """Icon from state, or boolean true/false icons (Filament ``IconColumn``)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._true_icon = "heroicon-o-check"
        self._false_icon = "heroicon-o-x-mark"
        self._size: str | None = None

    def true_icon(self, name: str) -> Self:
        self._true_icon = name
        return self

    def false_icon(self, name: str) -> Self:
        self._false_icon = name
        return self

    def size(self, value: str) -> Self:
        self._size = value
        return self

    def render_cell(self, record: Any, **ctx: Any) -> str:
        from almasix.orbit.support.icons import icon as render_icon

        value = self.resolve_state(record)
        if self._boolean:
            icon_name = self._true_icon if value else self._false_icon
        else:
            icon_name = str(value or "heroicon-o-check")
        color = self._resolve_color(record, value, **ctx)
        if self._boolean and color is None:
            color = "success" if value else "danger"
        size_c = f" or-icon-size-{e(self._size)}" if self._size else ""
        color_c = f" or-color-{color}" if color else ""
        return (
            f'<td class="{self._td_classes()}">'
            f'<span class="or-icon-column{size_c}{color_c}">{render_icon(icon_name)}</span>'
            f"</td>"
        )


class BooleanColumn(IconColumn):
    """Deprecated Filament alias — boolean icons (not Yes/No text)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._boolean = True


class ImageColumn(Column):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._circular = False
        self._size: str | int | None = None
        self._default_image_url: str | None = None
        self._stacked = False
        self._stacked_limit: int | None = None

    def circular(self, condition: bool = True) -> Self:
        self._circular = condition
        return self

    def size(self, value: str | int) -> Self:
        self._size = value
        return self

    def default_image_url(self, url: str) -> Self:
        self._default_image_url = url
        return self

    def stacked(self, condition: bool = True) -> Self:
        self._stacked = condition
        return self

    def limit(self, count: int) -> Self:  # type: ignore[override]
        self._stacked_limit = count
        return self

    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record)
        urls: list[str] = []
        if isinstance(value, (list, tuple)):
            urls = [str(u) for u in value if u]
        elif value:
            urls = [str(value)]
        if not urls and self._default_image_url:
            urls = [self._default_image_url]
        if not urls:
            return f'<td class="{self._td_classes()}"></td>'
        shape = " or-avatar-circle" if self._circular else " or-avatar-square"
        size_style = ""
        size_c = ""
        if self._size is not None:
            if isinstance(self._size, int) or str(self._size).isdigit():
                px = int(self._size)
                size_style = f' style="width:{px}px;height:{px}px"'
            else:
                size_c = f" or-avatar-{e(str(self._size))}"
        if self._stacked and len(urls) > 1:
            limit = self._stacked_limit if self._stacked_limit is not None else len(urls)
            shown = urls[:limit]
            extra = len(urls) - len(shown)
            imgs = "".join(
                f'<img class="or-avatar or-avatar-stacked{shape}{size_c}" src="{e(u)}" alt=""'
                f"{size_style} />"
                for u in shown
            )
            more = (
                f'<span class="or-avatar-more">+{extra}</span>' if extra > 0 else ""
            )
            return (
                f'<td class="{self._td_classes()}">'
                f'<div class="or-avatar-stack">{imgs}{more}</div></td>'
            )
        u = urls[0]
        return (
            f'<td class="{self._td_classes()}">'
            f'<img class="or-avatar{shape}{size_c}" src="{e(u)}" alt=""{size_style} /></td>'
        )


class ColorColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record) or "#000000"
        text = str(value)
        swatch = (
            f'<span class="or-color-swatch" style="background:{e(text)}" '
            f'title="{e(text)}"></span>'
        )
        if self._copyable:
            swatch = _copyable_wrap(swatch, text)
        return f'<td class="{self._td_classes()}">{swatch}</td>'


def _editable_attrs(column: Column, record: Any, kind: str) -> str:
    rid = _record_id(record)
    name = e(column.get_name() or "")
    disabled = " disabled" if column.is_disabled(record=record) else ""
    return (
        f' data-orbit-column-edit="{kind}" data-record-id="{e(rid)}" '
        f'data-column="{name}"{disabled}'
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
        attrs = _editable_attrs(self, record, "select")
        return (
            f'<td class="{self._td_classes()}">'
            f'<select class="or-select or-select-inline" name="{name}"{attrs}>'
            f'{"".join(options_html)}</select></td>'
        )


class TagsColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record) or []
        if isinstance(value, str):
            value = [v.strip() for v in value.split(",") if v.strip()]
        badges = "".join(f'<span class="or-badge">{e(v)}</span>' for v in value)
        return f'<td class="{self._td_classes()}">{badges}</td>'


class CheckboxColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record)
        name = e(self.get_name() or "")
        checked = " checked" if value else ""
        attrs = _editable_attrs(self, record, "checkbox")
        return (
            f'<td class="{self._td_classes()}">'
            f'<input type="checkbox" class="or-checkbox" name="{name}"'
            f"{checked}{attrs} /></td>"
        )


class TextInputColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record)
        name = e(self.get_name() or "")
        val = "" if value is None else e(str(value))
        attrs = _editable_attrs(self, record, "text")
        return (
            f'<td class="{self._td_classes()}">'
            f'<input class="or-input or-input-inline" name="{name}" '
            f'value="{val}"{attrs} /></td>'
        )


class ToggleColumn(Column):
    def render_cell(self, record: Any, **ctx: Any) -> str:
        value = self.resolve_state(record)
        name = e(self.get_name() or "")
        checked = " checked" if value else ""
        attrs = _editable_attrs(self, record, "toggle")
        return (
            f'<td class="{self._td_classes()}">'
            f'<input type="checkbox" class="or-toggle" name="{name}"'
            f"{checked}{attrs} /></td>"
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
        return f'<td class="{self._td_classes()}"><div class="or-view-column">{body}</div></td>'


class ColumnGroup(Component):
    """Shared header over child columns (Filament ``ColumnGroup``)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._columns: list[Column] = []

    @classmethod
    def make(  # type: ignore[override]
        cls,
        name: str | Sequence[Column] | None = None,
        columns: Sequence[Column] | None = None,
    ) -> Self:
        """Filament-shaped ``make('Label', [cols])`` or ``make([cols]).label(...)``."""
        if isinstance(name, (list, tuple)):
            inst = cls(None)
            inst.columns(list(name))
            return inst
        inst = cls(name if isinstance(name, str) else None)
        if columns is not None:
            inst.columns(list(columns))
        return inst

    def columns(self, cols: Sequence[Column]) -> Self:
        self._columns = list(cols)
        return self

    def get_columns(self) -> list[Column]:
        return list(self._columns)
