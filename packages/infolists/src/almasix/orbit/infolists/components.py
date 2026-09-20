"""Infolist entries — Filament 5–parity read-only description list components."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import date, datetime
from datetime import time as dt_time
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e
from almasix.orbit.support.icons import icon as render_icon


def _simple_markdown(text: str) -> str:
    """Tiny safe markdown subset: escape, then **bold**, *italic*, newlines."""
    out = e(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", out)
    out = out.replace("\n", "<br />")
    return out


def _copyable_wrap(
    inner: str,
    copy_text: str,
    *,
    message: str | None = None,
    duration: int | None = None,
) -> str:
    extra = ""
    if message:
        extra += f' data-copy-message="{e(message)}"'
    if duration is not None:
        extra += f' data-copy-message-duration="{e(duration)}"'
    return (
        f'<span class="or-copyable" data-copy="{e(copy_text)}"{extra} title="Copy">'
        f"{inner}"
        f'<button type="button" class="or-copy-btn" aria-label="Copy" '
        f'@click.stop="navigator.clipboard.writeText($el.closest(\'[data-copy]\').dataset.copy)">'
        f'<span class="or-copy-glyph" aria-hidden="true">⎘</span></button></span>'
    )


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return slug or "custom"


def _truncate_words(text: str, count: int, end: str) -> str:
    words = text.split()
    if len(words) <= count:
        return text
    return " ".join(words[:count]) + end


def _relative_time(value: Any) -> str:
    """Human-relative time, e.g. ``"just now"``, ``"5 minutes ago"``, ``"in 2 days"``."""
    dt_value: datetime | None = None
    if isinstance(value, datetime):
        dt_value = value
    elif isinstance(value, date):
        dt_value = datetime(value.year, value.month, value.day)
    else:
        text = str(value)
        try:
            dt_value = datetime.fromisoformat(text)
        except ValueError:
            return text
    now = datetime.now(dt_value.tzinfo) if dt_value.tzinfo else datetime.now()
    seconds = (now - dt_value).total_seconds()
    future = seconds < 0
    seconds = abs(seconds)
    if seconds < 45:
        return "just now"
    periods = (
        (365 * 24 * 3600, "year"),
        (30 * 24 * 3600, "month"),
        (7 * 24 * 3600, "week"),
        (24 * 3600, "day"),
        (3600, "hour"),
        (60, "minute"),
    )
    for period_seconds, label in periods:
        if seconds >= period_seconds:
            count = int(seconds // period_seconds)
            unit = label if count == 1 else f"{label}s"
            return f"in {count} {unit}" if future else f"{count} {unit} ago"
    count = int(seconds) or 1
    unit = "second" if count == 1 else "seconds"
    return f"in {count} {unit}" if future else f"{count} {unit} ago"


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


class Entry(Component):
    """Base infolist entry — shared chrome, formatters, and state resolution."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._state: Any = None
        self._has_custom_state = False
        self._placeholder: str | Callable[..., str] | None = None
        self._format_state: Callable[[Any], Any] | None = None
        self._url: str | Callable[..., str] | None = None
        self._open_url_in_new_tab = False
        self._copyable = False
        self._copy_message: str | Callable[..., str] | None = None
        self._copy_message_duration: int | None = None
        self._badge: bool | Callable[..., bool] = False
        self._color: str | Callable[..., str] | None = None
        self._icon: str | Callable[..., str] | None = None
        self._icon_position: str = "before"
        self._icon_color: str | Callable[..., str] | None = None
        self._tooltip: str | Callable[..., str] | None = None
        self._alignment: str = "start"
        self._extra_entry_wrapper_attributes: dict[str, Any] = {}
        self._prefix_action: str | None = None
        self._suffix_action: str | None = None
        self._money_currency: str | None = None
        self._money_divide_by: float | int = 1
        self._money_decimal_places: int = 2
        self._date_format: str | None = None
        self._time_only: bool = False
        self._since: bool = False
        self._numeric: bool = False
        self._numeric_decimal_places: int | None = None
        self._limit: int | None = None
        self._limit_end: str = "…"
        self._limit_words: int | None = None
        self._line_clamp: int | None = None
        self._wrap = False
        self._weight: str | None = None
        self._size: str | None = None
        self._font_family: str | None = None
        self._markdown = False
        self._html = False
        self._prose = False
        self._list_bullet = False
        self._separator: str | None = None
        self._above_label: str | Callable[..., str] | None = None
        self._below_label: str | Callable[..., str] | None = None
        self._before_label: str | Callable[..., str] | None = None
        self._after_label: str | Callable[..., str] | None = None
        self._above_content: str | Callable[..., str] | None = None
        self._below_content: str | Callable[..., str] | None = None
        self._before_content: str | Callable[..., str] | None = None
        self._after_content: str | Callable[..., str] | None = None

    # —— State ——

    def state(self, value: Any) -> Self:
        """Override entry state (static or callable)."""
        self._state = value
        self._has_custom_state = True
        return self

    def placeholder(self, text: str | Callable[..., str]) -> Self:
        """Display text when state is empty (not treated as real state)."""
        self._placeholder = text
        return self

    def format_state_using(self, callback: Callable[[Any], Any]) -> Self:
        self._format_state = callback
        return self

    def resolve_state(self, record: Any, **ctx: Any) -> Any:
        if self._has_custom_state:
            value = evaluate(self._state, record=record, **ctx)
        else:
            name = self.get_name() or ""
            value = dot_get(record, name) if name else None
        if (value is None or value == "") and self._default is not None:
            value = self.get_default(record=record, **ctx)
        if self._format_state:
            value = self._format_state(value)
        if isinstance(value, str):
            if self._limit is not None and len(value) > self._limit:
                value = value[: self._limit] + self._limit_end
            if self._limit_words is not None:
                value = _truncate_words(value, self._limit_words, self._limit_end)
        return value

    def _is_empty(self, value: Any) -> bool:
        return value is None or value == "" or (isinstance(value, (list, tuple)) and not value)

    def _resolved_placeholder(self, record: Any, **ctx: Any) -> str | None:
        if self._placeholder is None:
            return None
        result = evaluate(self._placeholder, record=record, **ctx)
        return None if result is None else str(result)

    # —— Link / copy / badge / icon ——

    def url(self, url: str | Callable[..., str]) -> Self:
        self._url = url
        return self

    def open_url_in_new_tab(self, condition: bool = True) -> Self:
        self._open_url_in_new_tab = condition
        return self

    def copyable(self, condition: bool = True) -> Self:
        self._copyable = condition
        return self

    def copy_message(self, message: str | Callable[..., str]) -> Self:
        self._copy_message = message
        return self

    def copy_message_duration(self, milliseconds: int) -> Self:
        self._copy_message_duration = milliseconds
        return self

    def badge(self, condition: bool | Callable[..., bool] = True) -> Self:
        self._badge = condition
        return self

    def color(self, color: str | Callable[..., str]) -> Self:
        self._color = color
        return self

    def icon(self, name: str | Callable[..., str]) -> Self:
        self._icon = name
        return self

    def icon_position(self, position: str) -> Self:
        self._icon_position = position
        return self

    def icon_color(self, color: str | Callable[..., str]) -> Self:
        self._icon_color = color
        return self

    def tooltip(self, text: str | Callable[..., str]) -> Self:
        self._tooltip = text
        return self

    def alignment(self, value: str) -> Self:
        self._alignment = value
        return self

    def align(self, value: str) -> Self:
        return self.alignment(value)

    def align_start(self) -> Self:
        return self.alignment("start")

    def align_center(self) -> Self:
        return self.alignment("center")

    def align_end(self) -> Self:
        return self.alignment("end")

    def extra_entry_wrapper_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_entry_wrapper_attributes.update(attrs)
        return self

    def prefix_action(self, action: str) -> Self:
        self._prefix_action = action
        return self

    def suffix_action(self, action: str) -> Self:
        self._suffix_action = action
        return self

    # —— Shared formatters (TextEntry pipeline) ——

    def money(
        self,
        currency: str = "USD",
        *,
        divide_by: float | int = 1,
        decimal_places: int = 2,
    ) -> Self:
        self._money_currency = currency
        self._money_divide_by = divide_by
        self._money_decimal_places = decimal_places
        return self

    def date(self, format: str = "%Y-%m-%d") -> Self:
        self._date_format = format
        self._time_only = False
        return self

    def date_time(self, format: str = "%Y-%m-%d %H:%M") -> Self:
        return self.date(format)

    def time(self, format: str = "%H:%M") -> Self:
        self._date_format = format
        self._time_only = True
        return self

    def since(self, condition: bool = True) -> Self:
        self._since = condition
        return self

    def numeric(self, decimal_places: int | None = None) -> Self:
        self._numeric = True
        self._numeric_decimal_places = decimal_places
        return self

    def limit(self, length: int, end: str = "…") -> Self:
        self._limit = length
        self._limit_end = end
        return self

    def words(self, count: int, end: str = "…") -> Self:
        self._limit_words = count
        self._limit_end = end
        return self

    def line_clamp(self, lines: int) -> Self:
        self._line_clamp = lines
        return self

    def wrap(self, condition: bool = True) -> Self:
        self._wrap = condition
        return self

    def weight(self, weight: str) -> Self:
        self._weight = weight
        return self

    def size(self, value: str) -> Self:
        self._size = value
        return self

    def font_family(self, name: str) -> Self:
        self._font_family = name
        return self

    def markdown(self, condition: bool = True) -> Self:
        self._markdown = condition
        return self

    def html(self, condition: bool = True) -> Self:
        self._html = condition
        return self

    def prose(self, condition: bool = True) -> Self:
        self._prose = condition
        return self

    def list_with_line_breaks(self, condition: bool = True) -> Self:
        self._list_bullet = condition
        return self

    def bulleted(self, condition: bool = True) -> Self:
        return self.list_with_line_breaks(condition)

    def separator(self, char: str) -> Self:
        self._separator = char
        return self

    # —— Content slots ——

    def above_label(self, content: str | Callable[..., str]) -> Self:
        self._above_label = content
        return self

    def below_label(self, content: str | Callable[..., str]) -> Self:
        self._below_label = content
        return self

    def before_label(self, content: str | Callable[..., str]) -> Self:
        self._before_label = content
        return self

    def after_label(self, content: str | Callable[..., str]) -> Self:
        self._after_label = content
        return self

    def above_content(self, content: str | Callable[..., str]) -> Self:
        self._above_content = content
        return self

    def below_content(self, content: str | Callable[..., str]) -> Self:
        self._below_content = content
        return self

    def before_content(self, content: str | Callable[..., str]) -> Self:
        self._before_content = content
        return self

    def after_content(self, content: str | Callable[..., str]) -> Self:
        self._after_content = content
        return self

    # —— Format / chrome helpers ——

    def _format_display_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (list, tuple)) and (self._list_bullet or self._separator):
            if self._separator:
                return self._separator.join(str(item) for item in value)
            return "\n".join(f"• {item}" for item in value)
        if self._money_currency is not None:
            try:
                num = float(value) / float(self._money_divide_by)
            except (TypeError, ValueError):
                return str(value)
            return f"{self._money_currency} {num:.{self._money_decimal_places}f}"
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
        if self._since:
            return _relative_time(value)
        if self._date_format is not None:
            if isinstance(value, datetime):
                return value.strftime(self._date_format)
            if isinstance(value, dt_time):
                return value.strftime(self._date_format)
            if isinstance(value, date):
                return value.strftime(self._date_format)
            text = str(value)
            try:
                if self._time_only:
                    for fmt in ("%H:%M:%S", "%H:%M"):
                        try:
                            return datetime.strptime(text, fmt).strftime(self._date_format)
                        except ValueError:
                            continue
                    return text
                if "T" in text:
                    return datetime.fromisoformat(text[:19]).strftime(self._date_format)
                return datetime.strptime(text[:10], "%Y-%m-%d").strftime(self._date_format)
            except ValueError:
                return text
        return str(value)

    def _resolve_color(self, record: Any, value: Any, **ctx: Any) -> str | None:
        color = self._color
        if callable(color):
            color = evaluate(color, record=record, state=value, **ctx)
        return str(color) if color else None

    def _resolve_badge(self, record: Any, value: Any, **ctx: Any) -> bool:
        badge = self._badge
        if callable(badge):
            return bool(evaluate(badge, record=record, state=value, **ctx))
        return bool(badge)

    def _resolved_tooltip(self, record: Any, value: Any, **ctx: Any) -> str | None:
        if self._tooltip is None:
            return None
        result = evaluate(self._tooltip, record=record, state=value, **ctx)
        return None if result is None else str(result)

    def _slot_html(self, content: str | Callable[..., str] | None, css: str, **ctx: Any) -> str:
        if content is None:
            return ""
        text = evaluate(content, **ctx)
        if text in (None, ""):
            return ""
        return f'<div class="{css}">{text}</div>'

    def _hint_html(self, **ctx: Any) -> str:
        hint = self.get_hint(**ctx)
        if not hint and not self._hint_icon:
            return ""
        icon = ""
        if self._hint_icon:
            icon = render_icon(self.get_hint_icon(**ctx) or str(self._hint_icon))
        text = f'<span class="or-hint-text">{e(hint)}</span>' if hint else ""
        return f'<div class="or-hint">{icon}{text}</div>'

    def _helper_html(self, **ctx: Any) -> str:
        helper_text = self.get_helper_text(**ctx)
        return f'<p class="or-helper">{e(helper_text)}</p>' if helper_text else ""

    def _action_btn(self, action: str, css: str) -> str:
        return (
            f'<button type="button" class="{css}" '
            f'wire:click="mountAction(\'{e(action)}\')">…</button>'
        )

    def _affix_wrap(self, control: str) -> str:
        if not self._prefix_action and not self._suffix_action:
            return control
        pre = (
            f'<span class="or-entry-prefix">{self._action_btn(self._prefix_action, "or-entry-action")}</span>'
            if self._prefix_action
            else ""
        )
        suf = (
            f'<span class="or-entry-suffix">{self._action_btn(self._suffix_action, "or-entry-action")}</span>'
            if self._suffix_action
            else ""
        )
        return f'<div class="or-entry-affix">{pre}{control}{suf}</div>'

    def wrap_entry(self, inner: str, *, record: Any = None, state: Any = None, **ctx: Any) -> str:
        """Build ``<div class="or-entry">`` chrome with label / dd / slots."""
        eval_ctx = {**ctx, "record": record, "state": state}
        align = self._alignment or "start"
        align_c = f" or-align-{align}" if align and align != "start" else ""
        inline = self.is_inline_label() or bool(ctx.get("inline_label"))
        inline_c = " or-entry-inline" if inline else ""
        wrapper_attrs = _attrs_to_html(
            {
                **self.get_extra_attributes(**eval_ctx),
                **{
                    k: evaluate(v, **eval_ctx)
                    for k, v in self._extra_entry_wrapper_attributes.items()
                },
            }
        )
        tip = self._resolved_tooltip(record, state, **ctx)
        title_attr = f' title="{e(tip)}"' if tip else ""

        if self.is_label_hidden():
            label_html = (
                f'<dt class="or-entry-label or-sr-only">{e(self.get_label(**eval_ctx))}</dt>'
            )
        else:
            before = self._slot_html(self._before_label, "or-before-label", **eval_ctx)
            after = self._slot_html(self._after_label, "or-after-label", **eval_ctx)
            label_html = (
                f"{before}<dt class=\"or-entry-label\">{e(self.get_label(**eval_ctx))}</dt>{after}"
            )

        body = (
            f"{self._slot_html(self._above_label, 'or-above-label', **eval_ctx)}"
            f"{label_html}"
            f"{self._slot_html(self._below_label, 'or-below-label', **eval_ctx)}"
            f"{self._hint_html(**eval_ctx)}"
            f"{self._slot_html(self._above_content, 'or-above-content', **eval_ctx)}"
            f"{self._slot_html(self._before_content, 'or-before-content', **eval_ctx)}"
            f'<dd class="or-entry-dd"{title_attr}>{self._affix_wrap(inner)}</dd>'
            f"{self._slot_html(self._after_content, 'or-after-content', **eval_ctx)}"
            f"{self._slot_html(self._below_content, 'or-below-content', **eval_ctx)}"
            f"{self._helper_html(**eval_ctx)}"
        )
        return f'<div class="or-entry{align_c}{inline_c}"{wrapper_attrs}>{body}</div>'

    def _render_formatted_value(
        self,
        record: Any,
        value: Any,
        *,
        using_placeholder: bool = False,
        text: str | None = None,
        **ctx: Any,
    ) -> str:
        """Shared TextEntry-style value markup (badge, icon, copy, url, prose)."""
        badge_condition = False if using_placeholder else self._resolve_badge(record, value, **ctx)
        if text is None:
            if using_placeholder:
                text = ""
            else:
                is_list_display = isinstance(value, (list, tuple)) and (
                    self._list_bullet or bool(self._separator)
                )
                if (
                    self._money_currency is not None
                    or self._date_format is not None
                    or self._numeric
                    or self._since
                    or is_list_display
                ):
                    text = self._format_display_value(value)
                else:
                    text = "" if value is None else str(value)

        display_value = value
        if self._separator and isinstance(display_value, str) and display_value and not using_placeholder:
            display_value = [p.strip() for p in display_value.split(self._separator) if p.strip()]

        if (
            self._separator
            and badge_condition
            and isinstance(display_value, (list, tuple))
            and display_value
            and not using_placeholder
        ):
            color = self._resolve_color(record, display_value, **ctx)
            color_c = f" or-color-{e(color)}" if color else ""
            badges = "".join(
                f'<span class="or-badge{color_c}">{e(item)}</span>' for item in display_value
            )
            return f'<span class="or-badge-list">{badges}</span>'

        is_list_display = isinstance(value, (list, tuple)) and (
            self._list_bullet or bool(self._separator)
        )
        css = "or-badge" if badge_condition else "or-entry-value"
        if using_placeholder:
            css += " or-entry-placeholder"
        if self._prose and not using_placeholder:
            css += " or-prose"
        color = None if using_placeholder else self._resolve_color(record, value, **ctx)
        color_c = f" or-color-{color}" if color else ""
        weight_c = f" or-font-{e(self._weight)}" if self._weight else ""
        wrap_c = " or-entry-wrap" if self._wrap else ""
        size_c = f" or-text-size-{_slugify(self._size)}" if self._size else ""
        line_clamp_c = (
            f" or-line-clamp or-line-clamp-{int(self._line_clamp)}" if self._line_clamp else ""
        )
        font_class = ""
        style_parts: list[str] = []
        if self._font_family:
            font_class = f" or-font-family-{_slugify(self._font_family)}"
            style_parts.append(f"font-family:{self._font_family}")
        style_attr = f' style="{e(";".join(style_parts))}"' if style_parts else ""

        if using_placeholder:
            body = e(text or "")
        elif self._html:
            body = str(text)
        elif self._markdown:
            body = _simple_markdown(text or "")
        else:
            body = e(text or "").replace("\n", "<br />") if is_list_display else e(text or "")

        icon_html = ""
        if self._icon is not None and not using_placeholder:
            icon_name = evaluate(self._icon, record=record, state=value, **ctx)
            if icon_name:
                icon_color = self._icon_color
                if callable(icon_color):
                    icon_color = evaluate(icon_color, record=record, state=value, **ctx)
                icon_color_c = f" or-color-{e(icon_color)}" if icon_color else ""
                icon_after_c = " or-entry-icon-after" if self._icon_position == "after" else ""
                icon_html = (
                    f'<span class="or-entry-icon{icon_after_c}{icon_color_c}">'
                    f"{render_icon(str(icon_name))}</span>"
                )
        content_html = (
            f"{body}{icon_html}" if self._icon_position == "after" else f"{icon_html}{body}"
        )
        inner = (
            f'<span class="{css}{color_c}{weight_c}{wrap_c}{size_c}{line_clamp_c}{font_class}"'
            f"{style_attr}>{content_html}</span>"
        )
        if self._copyable and text and not using_placeholder:
            copy_message = self._copy_message
            if callable(copy_message):
                copy_message = evaluate(copy_message, record=record, state=value, **ctx)
            inner = _copyable_wrap(
                inner,
                text,
                message=str(copy_message) if copy_message else None,
                duration=self._copy_message_duration,
            )
        href = None
        if self._url is not None and not using_placeholder:
            href = evaluate(self._url, record=record, state=value, **ctx)
        if href:
            target = ' target="_blank" rel="noopener noreferrer"' if self._open_url_in_new_tab else ""
            inner = f'<a class="or-entry-link" href="{e(href)}"{target}>{inner}</a>'
        return inner

    def _record_ctx(self, state: Any = None, **ctx: Any) -> tuple[Any, dict[str, Any]]:
        """Pull ``record`` out of kwargs so resolve_state isn't double-passed."""
        record = ctx.pop("record", state)
        ctx.pop("state", None)
        return record, ctx

    def render(self, state: Any = None, **ctx: Any) -> str:
        record, ctx = self._record_ctx(state, **ctx)
        value = self.resolve_state(record, **ctx) if record is not None else state
        using_placeholder = False
        text: str | None = None
        if self._is_empty(value):
            placeholder = self._resolved_placeholder(record, state=value, **ctx)
            if placeholder is not None:
                text = placeholder
                using_placeholder = True
            else:
                text = ""
        inner = self._render_formatted_value(
            record,
            value,
            using_placeholder=using_placeholder,
            text=text,
            **ctx,
        )
        return self.wrap_entry(inner, record=record, state=value, **ctx)


class TextEntry(Entry):
    """Default text entry — full format pipeline."""

    pass


class IconEntry(Entry):
    """Icon from state, or boolean true/false icons (Filament ``IconEntry``)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._boolean = False
        self._true_icon = "heroicon-o-check"
        self._false_icon = "heroicon-o-x-mark"
        self._true_color: str | Callable[..., str] | None = None
        self._false_color: str | Callable[..., str] | None = None
        self._icon_size: str | None = None

    def boolean(self, condition: bool = True) -> Self:
        self._boolean = condition
        return self

    def true_icon(self, name: str) -> Self:
        self._true_icon = name
        return self

    def false_icon(self, name: str) -> Self:
        self._false_icon = name
        return self

    def true_color(self, color: str | Callable[..., str]) -> Self:
        self._true_color = color
        return self

    def false_color(self, color: str | Callable[..., str]) -> Self:
        self._false_color = color
        return self

    def size(self, value: str) -> Self:  # type: ignore[override]
        self._icon_size = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        record, ctx = self._record_ctx(state, **ctx)
        value = self.resolve_state(record, **ctx) if record is not None else state
        if self._is_empty(value) and not self._boolean:
            placeholder = self._resolved_placeholder(record, state=value, **ctx)
            if placeholder is not None:
                inner = f'<span class="or-entry-value or-entry-placeholder">{e(placeholder)}</span>'
                return self.wrap_entry(inner, record=record, state=value, **ctx)
        if self._boolean:
            icon_name = self._true_icon if value else self._false_icon
        elif self._icon is not None:
            resolved = evaluate(self._icon, record=record, state=value, **ctx)
            icon_name = str(resolved or "heroicon-o-information-circle")
        else:
            icon_name = str(value or "heroicon-o-information-circle")
        color = self._resolve_color(record, value, **ctx)
        if self._boolean and color is None:
            state_color = self._true_color if value else self._false_color
            if callable(state_color):
                state_color = evaluate(state_color, record=record, state=value, **ctx)
            color = str(state_color) if state_color else ("success" if value else "danger")
        size_c = f" or-icon-size-{e(self._icon_size)}" if self._icon_size else ""
        color_c = f" or-color-{color}" if color else ""
        inner = (
            f'<span class="or-icon-entry{size_c}{color_c}">{render_icon(str(icon_name))}</span>'
        )
        return self.wrap_entry(inner, record=record, state=value, **ctx)


class ImageEntry(Entry):
    """Image / avatar entry with stacked support (Filament ``ImageEntry``)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._circular = False
        self._square = False
        self._image_size: str | int | None = None
        self._image_width: str | int | None = None
        self._image_height: str | int | None = None
        self._default_image_url: str | None = None
        self._stacked = False
        self._stacked_limit: int | None = None
        self._alt: str | Callable[..., str] | None = None
        self._ring: str | int | None = None
        self._overlap: str | int | None = None
        self._extra_img_attributes: dict[str, Any] = {}

    def circular(self, condition: bool = True) -> Self:
        self._circular = condition
        return self

    def square(self, condition: bool = True) -> Self:
        self._square = condition
        if condition:
            self._circular = False
        return self

    def size(self, value: str | int) -> Self:  # type: ignore[override]
        self._image_size = value
        return self

    def image_size(self, value: str | int) -> Self:
        return self.size(value)

    def width(self, value: str | int) -> Self:
        self._image_width = value
        return self

    def height(self, value: str | int) -> Self:
        self._image_height = value
        return self

    def default_image_url(self, url: str) -> Self:
        self._default_image_url = url
        return self

    def stacked(self, condition: bool = True) -> Self:
        self._stacked = condition
        return self

    def limit(self, count: int, end: str = "…") -> Self:  # type: ignore[override]
        self._stacked_limit = count
        return self

    def alt(self, text: str | Callable[..., str]) -> Self:
        self._alt = text
        return self

    def ring(self, width: str | int) -> Self:
        self._ring = width
        return self

    def overlap(self, amount: str | int) -> Self:
        self._overlap = amount
        return self

    def extra_img_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_img_attributes.update(attrs)
        return self

    def _resolved_alt(self, record: Any, **ctx: Any) -> str:
        if self._alt is None:
            return ""
        result = evaluate(self._alt, record=record, **ctx)
        return "" if result is None else str(result)

    def _extra_img_attrs_html(self, record: Any, **ctx: Any) -> str:
        if not self._extra_img_attributes:
            return ""
        attrs = {
            k: evaluate(v, record=record, **ctx) for k, v in self._extra_img_attributes.items()
        }
        return _attrs_to_html(attrs)

    def render(self, state: Any = None, **ctx: Any) -> str:
        record, ctx = self._record_ctx(state, **ctx)
        value = self.resolve_state(record, **ctx) if record is not None else state
        urls: list[str] = []
        if isinstance(value, (list, tuple)):
            urls = [str(u) for u in value if u]
        elif value:
            urls = [str(value)]
        if not urls and self._default_image_url:
            urls = [self._default_image_url]
        if not urls:
            placeholder = self._resolved_placeholder(record, state=value, **ctx)
            if placeholder is not None:
                inner = f'<span class="or-entry-value or-entry-placeholder">{e(placeholder)}</span>'
                return self.wrap_entry(inner, record=record, state=value, **ctx)
            return self.wrap_entry("", record=record, state=value, **ctx)

        shape = " or-avatar-circle" if self._circular else (" or-avatar-square" if self._square else "")
        base_style_parts: list[str] = []
        size_c = ""
        if self._image_size is not None:
            if isinstance(self._image_size, int) or str(self._image_size).isdigit():
                px = int(self._image_size)
                base_style_parts.append(f"width:{px}px;height:{px}px")
            else:
                size_c = f" or-avatar-{e(str(self._image_size))}"
        if self._image_width is not None:
            w = self._image_width
            base_style_parts.append(
                f"width:{w}px" if isinstance(w, int) or str(w).isdigit() else f"width:{w}"
            )
        if self._image_height is not None:
            h = self._image_height
            base_style_parts.append(
                f"height:{h}px" if isinstance(h, int) or str(h).isdigit() else f"height:{h}"
            )
        if self._ring is not None:
            ring = self._ring
            ring_px = f"{ring}px" if isinstance(ring, int) or str(ring).isdigit() else str(ring)
            base_style_parts.append(f"--or-avatar-ring:{ring_px}")
        alt = self._resolved_alt(record, **ctx)
        extra_attrs = self._extra_img_attrs_html(record, **ctx)

        if self._stacked and len(urls) > 1:
            limit = self._stacked_limit if self._stacked_limit is not None else len(urls)
            shown = urls[:limit]
            extra = len(urls) - len(shown)
            stack_style_parts = list(base_style_parts)
            if self._overlap is not None:
                amt = self._overlap
                amt_px = f"{amt}px" if isinstance(amt, int) or str(amt).isdigit() else str(amt)
                stack_style_parts.append(f"--or-avatar-overlap:{amt_px}")
            stack_style = f' style="{e(";".join(stack_style_parts))}"' if stack_style_parts else ""
            imgs = "".join(
                f'<img class="or-entry-image or-avatar or-avatar-stacked{shape}{size_c}" '
                f'src="{e(u)}" alt="{e(alt)}"{stack_style}{extra_attrs} />'
                for u in shown
            )
            more = f'<span class="or-avatar-more">+{extra}</span>' if extra > 0 else ""
            inner = f'<div class="or-avatar-stack">{imgs}{more}</div>'
            return self.wrap_entry(inner, record=record, state=value, **ctx)

        size_style = f' style="{e(";".join(base_style_parts))}"' if base_style_parts else ""
        u = urls[0]
        inner = (
            f'<img class="or-entry-image or-avatar{shape}{size_c}" src="{e(u)}" '
            f'alt="{e(alt)}"{size_style}{extra_attrs} />'
        )
        return self.wrap_entry(inner, record=record, state=value, **ctx)


class ColorEntry(Entry):
    """Color swatch entry with optional copyable."""

    def render(self, state: Any = None, **ctx: Any) -> str:
        record, ctx = self._record_ctx(state, **ctx)
        value = self.resolve_state(record, **ctx) if record is not None else state
        if self._is_empty(value):
            placeholder = self._resolved_placeholder(record, state=value, **ctx)
            if placeholder is not None:
                inner = f'<span class="or-entry-value or-entry-placeholder">{e(placeholder)}</span>'
                return self.wrap_entry(inner, record=record, state=value, **ctx)
            value = "#000000"
        text = str(value)
        swatch = (
            f'<span class="or-color-swatch" style="background:{e(text)}" '
            f'title="{e(text)}"></span> <span class="or-entry-value">{e(text)}</span>'
        )
        if self._copyable:
            copy_message = self._copy_message
            if callable(copy_message):
                copy_message = evaluate(copy_message, record=record, state=value, **ctx)
            swatch = _copyable_wrap(
                swatch,
                text,
                message=str(copy_message) if copy_message else None,
                duration=self._copy_message_duration,
            )
        return self.wrap_entry(swatch, record=record, state=value, **ctx)


class CodeEntry(Entry):
    """Monospace / code block entry."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._grammar: str | None = None

    def grammar(self, language: str) -> Self:
        self._grammar = language
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        record, ctx = self._record_ctx(state, **ctx)
        value = self.resolve_state(record, **ctx) if record is not None else state
        if isinstance(value, (dict, list)):
            text = json.dumps(value, indent=2, default=str)
        elif value is None:
            text = ""
        else:
            text = str(value)
        lang = f' data-language="{e(self._grammar)}"' if self._grammar else ""
        code = f'<pre class="or-code"{lang}><code>{e(text)}</code></pre>'
        if self._copyable and text:
            copy_message = self._copy_message
            if callable(copy_message):
                copy_message = evaluate(copy_message, record=record, state=value, **ctx)
            code = _copyable_wrap(
                code,
                text,
                message=str(copy_message) if copy_message else None,
                duration=self._copy_message_duration,
            )
        return self.wrap_entry(code, record=record, state=value, **ctx)


class KeyValueEntry(Entry):
    """Dict display as a two-column table."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._key_label: str = "Key"
        self._value_label: str = "Value"

    def key_label(self, label: str) -> Self:
        self._key_label = label
        return self

    def value_label(self, label: str) -> Self:
        self._value_label = label
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        record, ctx = self._record_ctx(state, **ctx)
        value = self.resolve_state(record, **ctx) if record is not None else state
        rows = ""
        if isinstance(value, dict):
            header = (
                f"<thead><tr><th>{e(self._key_label)}</th>"
                f"<th>{e(self._value_label)}</th></tr></thead>"
            )
            body = "".join(
                f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in value.items()
            )
            rows = f"{header}<tbody>{body}</tbody>"
        table = f'<table class="or-key-value">{rows}</table>'
        return self.wrap_entry(table, record=record, state=value, **ctx)


class RepeatableEntry(Entry):
    """Nested entry schema over a list of items."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._schema: list[Component] = []
        self._columns: int = 1
        self._contained: bool = True

    def schema(self, components: list[Component]) -> Self:
        self._schema = list(components)
        return self

    def columns(self, count: int) -> Self:
        self._columns = count
        return self

    def contained(self, condition: bool = True) -> Self:
        self._contained = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        record, ctx = self._record_ctx(state, **ctx)
        value = self.resolve_state(record, **ctx) if record is not None else state
        items = value if isinstance(value, (list, tuple)) else []
        blocks: list[str] = []
        for index, item in enumerate(items):
            parts: list[str] = []
            child_ctx = {k: v for k, v in ctx.items() if k != "index"}
            for entry in self._schema:
                parts.append(entry.render(item, record=item, index=index, **child_ctx))
            blocks.append(
                f'<div class="or-repeatable-item" data-index="{index}">{"".join(parts)}</div>'
            )
        body = "".join(blocks) or '<p class="or-empty">No items</p>'
        cols_c = f" or-repeatable-cols-{self._columns}" if self._columns and self._columns > 1 else ""
        contained_c = "" if self._contained else " or-repeatable-bare"
        inner = f'<div class="or-repeatable{cols_c}{contained_c}">{body}</div>'
        return self.wrap_entry(inner, record=record, state=value, **ctx)


class ViewEntry(Entry):
    """Custom HTML entry (Filament ``ViewEntry``)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._view_content: str | Callable[..., str] | None = None

    def view(self, html_or_callable: str | Callable[..., str]) -> Self:  # type: ignore[override]
        self._view_content = html_or_callable
        return self

    def content(self, html_or_callable: str | Callable[..., str]) -> Self:
        return self.view(html_or_callable)

    def render(self, state: Any = None, **ctx: Any) -> str:
        record, ctx = self._record_ctx(state, **ctx)
        value = self.resolve_state(record, **ctx) if record is not None else state
        html = ""
        if self._view_content is not None:
            result = evaluate(self._view_content, record=record, state=value, **ctx)
            html = "" if result is None else str(result)
        return self.wrap_entry(html, record=record, state=value, **ctx)
