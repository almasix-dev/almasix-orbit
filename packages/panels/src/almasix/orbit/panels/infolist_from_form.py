"""Build a view infolist that follows a resource form's layout."""

from __future__ import annotations

import json
from datetime import datetime
from html.parser import HTMLParser
from typing import Any

from almasix.orbit.infolists.components import (
    ColorEntry,
    ImageEntry,
    KeyValueEntry,
    RepeatableEntry,
    TextEntry,
)
from almasix.orbit.schemas.layouts import (
    Callout,
    EmptyState,
    Fieldset,
    Flex,
    Grid,
    Group,
    Layout,
    Section,
    Split,
    Tab,
    Tabs,
    Wizard,
    WizardStep,
)
from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e


def components_from_form(components: list[Component]) -> list[Component]:
    """Mirror form components as infolist components, preserving arrangement."""
    mirrored: list[Component] = []
    for component in components:
        entry = mirror_component(component)
        if entry is not None:
            mirrored.append(entry)
    return mirrored


def mirror_component(component: Component) -> Component | None:
    """One form component → the matching infolist component, or ``None`` to skip."""
    if isinstance(component, Tabs):
        return _mirror_tabs(component)
    if isinstance(component, Wizard):
        return _mirror_wizard(component)
    if isinstance(component, Layout):
        return _mirror_layout(component)
    return _entry_for_field(component)


def _entry_for_field(field: Component) -> Component | None:
    from almasix.orbit.forms.components import (
        Builder,
        Checkbox,
        ColorPicker,
        DatePicker,
        FileUpload,
        Hidden,
        KeyValue,
        MoneyInput,
        MorphToSelect,
        Placeholder,
        Repeater,
        RichEditor,
        Select,
        TagsInput,
    )

    name = field.get_name()
    if not name or isinstance(field, (Hidden, Placeholder)):
        return None
    if isinstance(field, MorphToSelect):
        entry = TextEntry.make(name).format_state_using(_morph_label(field))
    elif isinstance(field, Select) and field.get_relationship():
        entry = TextEntry.make(name).format_state_using(_relationship_label(field))
    elif isinstance(field, KeyValue):
        entry: Component = (
            KeyValueEntry.make(name)
            .key_label(getattr(field, "_key_label", "Key"))
            .value_label(getattr(field, "_value_label", "Value"))
            .format_state_using(_as_dict)
        )
    elif isinstance(field, Repeater):
        children = components_from_form(list(field.get_schema() or []))
        if isinstance(field, Builder):
            seen = {child.get_name() for child in children}
            for block in field.get_blocks():
                for child in components_from_form(list(block.get_schema() or [])):
                    if child.get_name() not in seen:
                        children.append(child)
                        seen.add(child.get_name())
            if not any(child.get_name() == "type" for child in children):
                children.insert(0, TextEntry.make("type").label("Block"))
        repeatable = RepeatableEntry.make(name).schema(children).format_state_using(_as_list)
        columns = getattr(field, "_grid_columns", None)
        if isinstance(columns, int) and columns > 1:
            repeatable.columns(columns)
        entry = repeatable
    elif isinstance(field, MoneyInput):
        entry = TextEntry.make(name).format_state_using(_money_label(field))
    elif isinstance(field, TagsInput):
        entry = TextEntry.make(name).html().format_state_using(_tags_html(field))
    elif isinstance(field, Checkbox):
        entry = (
            TextEntry.make(name)
            .badge()
            .color(lambda state, **_: "success" if state == "Yes" else "danger")
            .format_state_using(_yes_no)
        )
    elif isinstance(field, ColorPicker):
        entry = ColorEntry.make(name)
    elif isinstance(field, DatePicker) and field._mode in {"date", "datetime", "time"}:
        entry = TextEntry.make(name).format_state_using(_temporal_label(field))
    elif isinstance(field, FileUpload) and _shows_image(field):
        entry = ImageEntry.make(name).lightbox().gallery().format_state_using(_upload_src)
        if field._avatar:
            entry.circular().size(96)
    elif isinstance(field, RichEditor):
        entry = TextEntry.make(name).html().format_state_using(_rich_html)
    else:
        entry = TextEntry.make(name)
    label = field.get_label()
    if label:
        entry.label(label)
    span = getattr(field, "_column_span", None)
    if span:
        entry.column_span(span)
    return entry


def _relationship_label(field: Any) -> Any:
    """Format a Many2One id as the related record's display field."""

    def format_value(value: Any) -> str:
        if value in (None, ""):
            return ""
        keys = value if isinstance(value, (list, tuple)) else [value]
        labels = field.resolve_relationship_options(value)
        names = [str(labels.get(str(key)) or key) for key in keys if key not in (None, "")]
        return ", ".join(names)

    return format_value


def _morph_label(field: Any) -> Any:
    """Format ``{type, id}`` as the related record's display field."""

    def format_value(value: Any) -> str:
        parsed = _parse_json(value)
        if not isinstance(parsed, dict):
            return "" if value in (None, "") else str(value)
        type_key = getattr(field, "_type_field", "type")
        id_key = getattr(field, "_id_field", "id")
        morph_type = str(parsed.get(type_key) or "")
        morph_id = parsed.get(id_key)
        type_label = morph_type
        model = None
        title = str(getattr(field, "_title_attribute", None) or "name")
        for item in field.get_types():
            if not isinstance(item, dict):
                continue
            key = str(item.get("type") or item.get("value") or item.get("name") or "")
            if key != morph_type:
                continue
            type_label = str(item.get("label") or morph_type)
            model = item.get("model")
            if item.get("title_attribute"):
                title = str(item["title_attribute"])
            break
        name = ""
        if isinstance(model, type) and morph_id not in (None, ""):
            from almasix.orbit.forms.select_relationship import load_relationship_options

            labels = load_relationship_options(
                model=model, title_attribute=title, keys=[morph_id]
            )
            name = labels.get(str(morph_id), "")
        if not name and morph_type:
            try:
                options = field.get_options_for_type(morph_type)
            except Exception:
                options = {}
            if isinstance(options, dict):
                raw = options.get(morph_id, options.get(str(morph_id)))
                name = "" if raw is None else str(raw)
        if name and type_label:
            return f"{type_label} · {name}"
        return "" if morph_id in (None, "") else str(morph_id)

    return format_value


_CURRENCY_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£", "KES": "KSh"}
_RICH_TAGS = {
    "p", "br", "strong", "b", "em", "i", "u", "s", "a", "h1", "h2", "h3",
    "blockquote", "ul", "ol", "li", "code", "pre", "hr", "img", "span",
}
_RICH_VOID = {"br", "hr", "img"}
_RICH_SKIP = {"script", "style", "iframe", "object", "embed"}


def _shows_image(field: Any) -> bool:
    """Avatar and ``.image()`` uploads display as pictures on the view."""
    if field._avatar:
        return True
    if not field._image_preview:
        return False
    types = [str(item) for item in (field._accepted_file_types or [])]
    if not types:
        return False
    return all(item == "image/*" or item.startswith("image/") for item in types)


def _upload_src(value: Any) -> str | list[str]:
    """Turn a stored upload path into the image URL the browser can load."""
    from almasix.orbit.forms.uploads import public_upload_url

    parsed = _parse_json(value)
    items = list(parsed) if isinstance(parsed, (list, tuple)) else [parsed]
    urls: list[str] = []
    for item in items:
        if isinstance(item, dict):
            item = item.get("url") or item.get("path") or ""
        text = "" if item in (None, "") else str(item).strip()
        if text:
            urls.append(public_upload_url(text))
    if len(urls) > 1:
        return urls
    return urls[0] if urls else ""


def _money_label(field: Any) -> Any:
    """Format an amount with its currency symbol."""

    def format_value(value: Any) -> str:
        if value in (None, ""):
            return ""
        try:
            amount = float(value)
        except (TypeError, ValueError):
            return str(value)
        code = str(getattr(field, "_currency", None) or "USD").upper()
        prefix = getattr(field, "_prefix", None)
        symbol = prefix if isinstance(prefix, str) and prefix.strip() else _CURRENCY_SYMBOLS.get(code, f"{code} ")
        sign = "-" if amount < 0 else ""
        return f"{sign}{symbol}{abs(amount):,.2f}"

    return format_value


def _tags_html(field: Any) -> Any:
    """Render tag values as read-only chips."""

    def format_value(value: Any) -> str:
        parsed = _parse_json(value)
        if isinstance(parsed, (list, tuple)):
            items = list(parsed)
        elif isinstance(parsed, str) and parsed.strip():
            sep = str(getattr(field, "_separator", None) or ",")
            items = [part.strip() for part in parsed.split(sep) if part.strip()]
        else:
            return ""
        prefix = str(getattr(field, "_tag_prefix", None) or "")
        suffix = str(getattr(field, "_tag_suffix", None) or "")
        chips: list[str] = []
        for item in items:
            if item in (None, ""):
                continue
            pre = f'<span class="or-tag-prefix">{e(prefix)}</span>' if prefix else ""
            suf = f'<span class="or-tag-suffix">{e(suffix)}</span>' if suffix else ""
            chips.append(
                f'<span class="or-tag">{pre}<span class="or-tag-label">{e(item)}</span>{suf}</span>'
            )
        if not chips:
            return ""
        return f'<span class="or-tags-readonly">{"".join(chips)}</span>'

    return format_value


def _yes_no(value: Any) -> str:
    if isinstance(value, str):
        return "Yes" if value.strip().lower() in {"1", "true", "yes", "on"} else "No"
    return "Yes" if value else "No"


def _temporal_label(field: Any) -> Any:
    """Format a date or time the way the picker displays it."""

    def format_value(value: Any) -> str:
        if value in (None, ""):
            return ""
        mode = str(getattr(field, "_mode", "date"))
        seconds = bool(getattr(field, "_seconds", False))
        parsed = _parse_temporal(value, mode)
        if parsed is None:
            return str(value)
        day = parsed.strftime("%B") + f" {parsed.day}, " + parsed.strftime("%Y")
        clock = parsed.strftime("%I:%M:%S %p") if seconds else parsed.strftime("%I:%M %p")
        if mode == "time":
            return clock
        if mode == "datetime":
            return f"{day} {clock}"
        return day

    return format_value


def _parse_temporal(value: Any, mode: str) -> datetime | None:
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    patterns = {
        "time": ("%H:%M:%S", "%I:%M:%S %p", "%H:%M", "%I:%M %p"),
        "datetime": (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M",
        ),
        "date": ("%Y-%m-%d",),
    }
    for pattern in patterns.get(mode, ("%Y-%m-%d",)):
        try:
            return datetime.strptime(text[:19] if mode != "time" else text, pattern)
        except ValueError:
            continue
    return None


class _RichSanitizer(HTMLParser):
    """Allow rich-text markup and drop scripts, handlers, and unsafe URLs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in _RICH_SKIP:
            self._skip += 1
            return
        if self._skip or tag not in _RICH_TAGS:
            return
        kept: list[str] = []
        for name, raw in attrs:
            key = name.lower()
            if key.startswith("on") or key not in {"href", "src", "alt", "title"}:
                continue
            if raw is None or (key in {"href", "src"} and not _safe_url(raw)):
                continue
            kept.append(f' {key}="{e(raw)}"')
        self.parts.append(f"<{tag}{''.join(kept)}{' />' if tag in _RICH_VOID else '>'}")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _RICH_SKIP:
            if self._skip:
                self._skip -= 1
            return
        if self._skip or tag not in _RICH_TAGS or tag in _RICH_VOID:
            return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(e(data))


def _safe_url(value: str) -> bool:
    text = value.strip().lower()
    if text.startswith(("javascript:", "data:", "vbscript:")):
        return False
    return True


def _rich_html(value: Any) -> str:
    if value in (None, ""):
        return ""
    parser = _RichSanitizer()
    parser.feed(str(value))
    parser.close()
    return "".join(parser.parts)


def _as_dict(value: Any) -> dict[str, Any]:
    parsed = _parse_json(value)
    return parsed if isinstance(parsed, dict) else {}


def _as_list(value: Any) -> list[Any]:
    parsed = _parse_json(value)
    return parsed if isinstance(parsed, list) else []


def _parse_json(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text or text[0] not in "[{":
        return value
    try:
        return json.loads(text)
    except Exception:
        return value


def _mirror_layout(layout: Layout) -> Layout:
    clone = type(layout).make(layout.get_name())
    _copy_common(layout, clone)
    if isinstance(layout, Section):
        if layout._heading:
            clone.heading(layout._heading)
        if layout._description:
            clone.description(layout._description)
        if layout._icon:
            clone.icon(layout._icon)
        clone.collapsible(layout._collapsible).collapsed(layout._collapsed)
        clone.compact(layout._compact).aside(layout._aside).secondary(layout._secondary)
    elif isinstance(layout, Grid):
        clone.columns(layout._columns)
        if layout._grid_container:
            clone.grid_container()
    elif isinstance(layout, Flex):
        clone.grow(layout._grow)
        if layout._from:
            clone.from_breakpoint(layout._from)
    elif isinstance(layout, Group):
        if layout._columns:
            clone.columns(layout._columns)
    elif isinstance(layout, Split):
        if layout._from:
            clone.from_(layout._from)
    elif isinstance(layout, Fieldset):
        clone.contained(layout._contained)
    elif isinstance(layout, Callout):
        if layout._description:
            clone.description(layout._description)
        clone.status(layout._status)
        if layout._color:
            clone.color(layout._color)
        if layout._icon:
            clone.icon(layout._icon)
        if layout._icon_color:
            clone.icon_color(layout._icon_color)
        if layout._footer_actions:
            clone.footer_actions(layout._footer_actions)
        clone.footer_actions_alignment(layout._footer_alignment)
    elif isinstance(layout, EmptyState):
        if layout._heading:
            clone.heading(layout._heading)
        if layout._description:
            clone.description(layout._description)
        if layout._icon:
            clone.icon(layout._icon)
        if layout._actions:
            clone.actions(layout._actions)
    label = layout.get_label()
    if label:
        clone.label(label)
    clone.schema(components_from_form(list(layout.get_child_components())))
    return clone


def _mirror_tabs(tabs: Tabs) -> Tabs:
    clone = Tabs.make(tabs.get_name())
    _copy_common(tabs, clone)
    clone.persist_tab(tabs._persist_tab).active_tab(tabs._active_tab)
    clone.tabs(*[_mirror_tab(tab) for tab in tabs._tabs])
    return clone


def _mirror_tab(tab: Tab) -> Tab:
    mirrored = Tab.make(tab.get_name())
    if tab._label is not None:
        mirrored.label(tab._label)
    if tab._icon:
        mirrored.icon(tab._icon)
    if tab._badge is not None:
        mirrored.badge(tab._badge)
    if tab._badge_color:
        mirrored.badge_color(tab._badge_color)
    if tab._extra_attributes:
        mirrored.extra_attributes(dict(tab._extra_attributes))
    mirrored.schema(components_from_form(list(tab.get_child_components())))
    return mirrored


def _mirror_wizard(wizard: Wizard) -> Wizard:
    clone = Wizard.make(wizard.get_name())
    _copy_common(wizard, clone)
    clone.start_step(wizard._start_step)
    clone.skippable(wizard._skippable)
    # A view has no fields to validate, so later steps must stay reachable.
    clone.non_linear()
    clone.vertical(wizard._vertical)
    clone.steps(*[_mirror_step(step) for step in wizard._steps])
    return clone


def _mirror_step(step: WizardStep) -> WizardStep:
    mirrored = WizardStep.make(step.get_name())
    if step._label is not None:
        mirrored.label(step._label)
    if step._description:
        mirrored.description(step._description)
    if step._icon:
        mirrored.icon(step._icon)
    if step._completed_icon:
        mirrored.completed_icon(step._completed_icon)
    if step._extra_attributes:
        mirrored.extra_attributes(dict(step._extra_attributes))
    mirrored.schema(components_from_form(list(step.get_child_components())))
    return mirrored


def _copy_common(source: Component, target: Component) -> None:
    if source._column_span:
        target.column_span(source._column_span)
    if isinstance(source, Layout) and isinstance(target, Layout):
        target.dense(source._dense).gap(source._gap)
