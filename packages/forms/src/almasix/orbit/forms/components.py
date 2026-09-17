"""Form fields — Filament-familiar fluent API."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e


def _flatten_options(raw: Any) -> dict[Any, Any]:
    """Flatten option groups into a value → label map."""
    if raw is None:
        return {}
    if callable(raw):
        return {}
    if isinstance(raw, Mapping):
        flat: dict[Any, Any] = {}
        for key, value in raw.items():
            if isinstance(value, Mapping):
                flat.update(_flatten_options(value))
            else:
                flat[key] = value
        return flat
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        flat = {}
        for item in raw:
            if isinstance(item, Mapping) and "options" in item:
                opts = item.get("options") or {}
                if isinstance(opts, Mapping):
                    flat.update(_flatten_options(opts))
            elif isinstance(item, Mapping) and "value" in item:
                flat[item["value"]] = item.get("label", item["value"])
        return flat
    try:
        return dict(raw) if raw else {}
    except (TypeError, ValueError):
        return {}


def _option_groups(raw: Any) -> list[tuple[str | None, dict[Any, Any]]]:
    """Return ``[(group_label|None, {value: label})]`` for select rendering."""
    if raw is None:
        return [(None, {})]
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        groups: list[tuple[str | None, dict[Any, Any]]] = []
        for item in raw:
            if isinstance(item, Mapping) and "options" in item:
                label = item.get("label")
                opts = item.get("options") or {}
                groups.append((None if label is None else str(label), dict(opts) if isinstance(opts, Mapping) else {}))
            elif isinstance(item, Mapping) and "value" in item:
                groups.append((None, {item["value"]: item.get("label", item["value"])}))
        return groups or [(None, {})]
    if isinstance(raw, Mapping):
        if raw and all(isinstance(v, Mapping) for v in raw.values()):
            return [(str(k), dict(v)) for k, v in raw.items()]
        return [(None, dict(raw))]
    return [(None, _flatten_options(raw))]


class Field(Component):
    """Base form field."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._rules: list[str | Callable[..., Any]] = []
        self._required: bool | Callable[..., bool] = False
        self._placeholder: str | Callable[..., str] | None = None
        self._autocomplete: str | None = None
        self._options: Any = {}
        self._multiple = False
        self._searchable = False
        self._relationship: dict[str, Any] | tuple[str, str] | None = None
        self._input_type = "text"
        self._rows: int | None = None
        self._accepted_file_types: list[str] = []
        self._max_size: int | None = None
        self._readonly = False
        self._validation_attribute: str | Callable[..., str] | None = None
        self._validation_messages: dict[str, str] = {}
        self._prefix: str | Callable[..., str] | None = None
        self._suffix: str | Callable[..., str] | None = None
        self._prefix_icon: str | None = None
        self._suffix_icon: str | None = None
        self._autofocus = False
        self._extra_input_attributes: dict[str, Any] = {}
        self._extra_field_wrapper_attributes: dict[str, Any] = {}
        self._after_state_updated: Callable[..., Any] | None = None
        self._after_state_updated_js: str | None = None
        self._dehydrate_state_using: Callable[..., Any] | None = None
        self._hint_action: str | None = None
        self._prefix_action: str | None = None
        self._suffix_action: str | None = None
        self._input_mode: str | None = None
        self._step: float | int | str | None = None
        self._min_value: float | int | None = None
        self._max_value: float | int | None = None
        self._option_descriptions: dict[str, str] = {}
        self._options_columns: int | None = None

    def rules(self, *rules: str | Callable[..., Any]) -> Self:
        self._rules.extend(rules)
        return self

    def get_rules(self, **ctx: Any) -> list[str | Callable[..., Any]]:
        rules = list(self._rules)
        if self.is_required(**ctx) and "required" not in [r for r in rules if isinstance(r, str)]:
            rules.insert(0, "required")
        return rules

    def required(self, condition: bool | Callable[..., bool] = True) -> Self:
        self._required = condition
        return self

    def is_required(self, **ctx: Any) -> bool:
        return bool(evaluate(self._required, **ctx))

    def readonly(self, condition: bool = True) -> Self:
        self._readonly = condition
        return self

    def is_readonly(self) -> bool:
        return self._readonly

    def placeholder(self, text: str | Callable[..., str]) -> Self:
        self._placeholder = text
        return self

    def get_placeholder(self, **ctx: Any) -> str | None:
        if self._placeholder is None:
            return None
        result = evaluate(self._placeholder, **ctx)
        return None if result is None else str(result)

    def autocomplete(self, value: str) -> Self:
        self._autocomplete = value
        return self

    def autofocus(self, condition: bool = True) -> Self:
        self._autofocus = condition
        return self

    def prefix(self, text: str | Callable[..., str]) -> Self:
        self._prefix = text
        return self

    def suffix(self, text: str | Callable[..., str]) -> Self:
        self._suffix = text
        return self

    def prefix_icon(self, icon: str) -> Self:
        self._prefix_icon = icon
        return self

    def suffix_icon(self, icon: str) -> Self:
        self._suffix_icon = icon
        return self

    def hint_action(self, action: str) -> Self:
        self._hint_action = action
        return self

    def prefix_action(self, action: str) -> Self:
        self._prefix_action = action
        return self

    def suffix_action(self, action: str) -> Self:
        self._suffix_action = action
        return self

    def descriptions(self, mapping: dict[str, str]) -> Self:
        """Per-option helper text for Radio / CheckboxList / ToggleButtons."""
        self._option_descriptions = dict(mapping)
        return self

    def options_columns(self, count: int) -> Self:
        self._options_columns = count
        return self

    def required_if(self, field: str, value: Any) -> Self:
        return self.rules(f"required_if:{field},{value}")

    def required_unless(self, field: str, value: Any) -> Self:
        return self.rules(f"required_unless:{field},{value}")

    def prohibited(self, condition: bool = True) -> Self:
        if condition:
            return self.rules("prohibited")
        return self

    def prohibited_if(self, field: str, value: Any) -> Self:
        return self.rules(f"prohibited_if:{field},{value}")

    def extra_input_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_input_attributes.update(attrs)
        return self

    def extra_field_wrapper_attributes(self, attrs: dict[str, Any]) -> Self:
        self._extra_field_wrapper_attributes.update(attrs)
        return self

    def after_state_updated(self, callback: Callable[..., Any]) -> Self:
        self._after_state_updated = callback
        return self

    def after_state_updated_js(self, script: str) -> Self:
        self._after_state_updated_js = script
        return self

    def dehydrate_state_using(self, callback: Callable[..., Any]) -> Self:
        self._dehydrate_state_using = callback
        return self

    def get_dehydrate_state_using(self) -> Callable[..., Any] | None:
        return self._dehydrate_state_using

    def input_mode(self, mode: str) -> Self:
        self._input_mode = mode
        return self

    def step(self, value: float | int | str) -> Self:
        self._step = value
        return self

    def min_value(self, value: float | int) -> Self:
        self._min_value = value
        return self

    def max_value(self, value: float | int) -> Self:
        self._max_value = value
        return self

    def unique(
        self,
        table: str,
        column: str | None = None,
        *,
        ignore: Any = None,
    ) -> Self:
        parts = [table]
        if column:
            parts.append(column)
        if ignore is not None:
            parts.append(str(ignore))
        return self.rules("unique:" + ",".join(parts))

    def exists(self, table: str, column: str | None = None) -> Self:
        body = table if column is None else f"{table},{column}"
        return self.rules(f"exists:{body}")

    def distinct(self) -> Self:
        return self.rules("distinct")

    def regex(self, pattern: str) -> Self:
        return self.rules(f"regex:{pattern}")

    def between(self, lo: float | int, hi: float | int) -> Self:
        return self.rules(f"between:{lo},{hi}")

    def options(self, options: Any) -> Self:
        self._options = options
        return self

    def enum(self, enum_cls: Any) -> Self:
        """Populate options from an ``Enum`` (value → name/label)."""
        try:
            from enum import Enum

            if isinstance(enum_cls, type) and issubclass(enum_cls, Enum):
                self._options = {member.value: member.name.replace("_", " ").title() for member in enum_cls}
                return self
        except TypeError:
            pass
        return self.options(enum_cls)

    def get_options(self, **ctx: Any) -> dict[Any, Any]:
        opts = evaluate(self._options, **ctx) if callable(self._options) else self._options
        return _flatten_options(opts)

    def get_option_groups(self, **ctx: Any) -> list[tuple[str | None, dict[Any, Any]]]:
        opts = evaluate(self._options, **ctx) if callable(self._options) else self._options
        return _option_groups(opts)

    def multiple(self, condition: bool = True) -> Self:
        self._multiple = condition
        return self

    def searchable(self, condition: bool = True) -> Self:
        self._searchable = condition
        return self

    def relationship(
        self,
        name: str,
        title_attribute: str,
        *,
        search_columns: Sequence[str] | None = None,
        preload: bool = False,
        modify_query: Callable[..., Any] | None = None,
        get_option_label: Callable[..., Any] | None = None,
    ) -> Self:
        self._relationship = {
            "name": name,
            "title_attribute": title_attribute,
            "search_columns": list(search_columns) if search_columns else None,
            "preload": preload,
            "modify_query": modify_query,
            "get_option_label": get_option_label,
        }
        return self

    def get_relationship(self) -> dict[str, Any] | None:
        if self._relationship is None:
            return None
        if isinstance(self._relationship, tuple):
            return {"name": self._relationship[0], "title_attribute": self._relationship[1]}
        return dict(self._relationship)

    def validation_attribute(self, name: str | Callable[..., str]) -> Self:
        self._validation_attribute = name
        return self

    def get_validation_attribute(self, **ctx: Any) -> str | None:
        if self._validation_attribute is None:
            return None
        result = evaluate(self._validation_attribute, **ctx)
        return None if result is None else str(result)

    def validation_messages(self, messages: Mapping[str, str]) -> Self:
        self._validation_messages.update(dict(messages))
        return self

    def format_validation_message(self, key: str, attr: str, default: str, **repl: Any) -> str:
        template = self._validation_messages.get(key, default)
        out = template.replace(":attribute", attr).replace("{attribute}", attr)
        for k, v in repl.items():
            out = out.replace(f":{k}", str(v)).replace(f"{{{k}}}", str(v))
        return out

    def email(self) -> Self:
        self._input_type = "email"
        return self.rules("email")

    def password(self) -> Self:
        self._input_type = "password"
        return self

    def numeric(self) -> Self:
        self._input_type = "number"
        return self.rules("numeric")

    def tel(self) -> Self:
        self._input_type = "tel"
        return self

    def url(self) -> Self:
        self._input_type = "url"
        return self.rules("url")

    def integer(self) -> Self:
        return self.numeric().rules("integer")

    def max_length(self, length: int) -> Self:
        return self.rules(f"max:{length}")

    def min_length(self, length: int) -> Self:
        return self.rules(f"min:{length}")

    def rows(self, count: int) -> Self:
        self._rows = count
        return self

    def accepted_file_types(self, types: Sequence[str]) -> Self:
        self._accepted_file_types = list(types)
        return self

    def max_size(self, kilobytes: int) -> Self:
        self._max_size = kilobytes
        return self

    def _attrs_to_html(self, attrs: dict[str, Any]) -> str:
        parts = []
        for key, value in attrs.items():
            if value is True:
                parts.append(e(str(key)))
            elif value is False or value is None:
                continue
            else:
                parts.append(f'{e(str(key))}="{e(value)}"')
        return (" " + " ".join(parts)) if parts else ""

    def _wire_binding(self, name: str) -> str:
        return self.wire_model_attrs(name)

    def _common_input_attrs(self, **ctx: Any) -> str:
        parts: list[str] = []
        if self._autocomplete:
            parts.append(f'autocomplete="{e(self._autocomplete)}"')
        if self._autofocus:
            parts.append("autofocus")
        if self._input_mode:
            parts.append(f'inputmode="{e(self._input_mode)}"')
        if self._step is not None:
            parts.append(f'step="{e(self._step)}"')
        if self._min_value is not None:
            parts.append(f'min="{e(self._min_value)}"')
        if self._max_value is not None:
            parts.append(f'max="{e(self._max_value)}"')
        parts.append(self._attrs_to_html(self._extra_input_attributes).strip())
        return (" " + " ".join(p for p in parts if p)) if any(parts) else ""

    def _label_html(self, name: str, **ctx: Any) -> str:
        if self._hidden_label:
            return f'<label class="or-label or-sr-only" for="or-{name}">{e(self.get_label(**ctx))}</label>'
        req = ' <span class="or-required">*</span>' if self.is_required(**ctx) else ""
        return f'<label class="or-label" for="or-{name}">{e(self.get_label(**ctx))}{req}</label>'

    def _hint_html(self, **ctx: Any) -> str:
        hint = self.get_hint(**ctx)
        if not hint and not self._hint_icon and not self._hint_action:
            return ""
        icon = ""
        if self._hint_icon:
            from almasix.orbit.support.icons import icon as render_icon

            icon = render_icon(self.get_hint_icon(**ctx) or self._hint_icon)
        action = ""
        if self._hint_action:
            action = (
                f'<button type="button" class="or-hint-action" '
                f'wire:click="mountAction(\'{e(self._hint_action)}\')">?</button>'
            )
        text = f'<span class="or-hint-text">{e(hint)}</span>' if hint else ""
        return f'<div class="or-hint">{icon}{text}{action}</div>'

    def _helper_html(self, **ctx: Any) -> str:
        helper_text = self.get_helper_text(**ctx)
        return f'<p class="or-helper">{e(helper_text)}</p>' if helper_text else ""

    def _affix_wrap(self, control: str, **ctx: Any) -> str:
        prefix = evaluate(self._prefix, **ctx) if self._prefix is not None else None
        suffix = evaluate(self._suffix, **ctx) if self._suffix is not None else None
        has_affix = (
            prefix
            or suffix
            or self._prefix_icon
            or self._suffix_icon
            or self._prefix_action
            or self._suffix_action
        )
        if not has_affix:
            return control
        pre = ""
        if self._prefix_icon or prefix or self._prefix_action:
            from almasix.orbit.support.icons import icon as render_icon

            icon = render_icon(self._prefix_icon) if self._prefix_icon else ""
            text = f'<span class="or-affix-text">{e(prefix)}</span>' if prefix else ""
            act = ""
            if self._prefix_action:
                act = (
                    f'<button type="button" class="or-affix-action" '
                    f'wire:click="mountAction(\'{e(self._prefix_action)}\')">…</button>'
                )
            pre = f'<span class="or-input-prefix">{icon}{text}{act}</span>'
        suf = ""
        if self._suffix_icon or suffix or self._suffix_action:
            from almasix.orbit.support.icons import icon as render_icon

            icon = render_icon(self._suffix_icon) if self._suffix_icon else ""
            text = f'<span class="or-affix-text">{e(suffix)}</span>' if suffix else ""
            act = ""
            if self._suffix_action:
                act = (
                    f'<button type="button" class="or-affix-action" '
                    f'wire:click="mountAction(\'{e(self._suffix_action)}\')">…</button>'
                )
            suf = f'<span class="or-input-suffix">{icon}{text}{act}</span>'
        return f'<div class="or-input-affix">{pre}{control}{suf}</div>'

    def _after_state_attr(self) -> str:
        if self._after_state_updated_js:
            return f' x-on:change="{e(self._after_state_updated_js)}"'
        if self._after_state_updated is not None:
            return ' data-after-state-updated="true"'
        return ""

    def wrap_field(self, name: str, control: str, **ctx: Any) -> str:
        """Shared field chrome: label, hint, helper, wrapper attributes, inline label."""
        inline = " or-field-inline" if self._inline_label else ""
        wrapper_attrs = self._attrs_to_html(
            {**self.get_extra_attributes(**ctx), **{
                k: evaluate(v, **ctx) for k, v in self._extra_field_wrapper_attributes.items()
            }}
        )
        body = (
            f"{self._label_html(name, **ctx)}{self._hint_html(**ctx)}"
            f"{self._affix_wrap(control, **ctx)}{self._helper_html(**ctx)}"
        )
        return (
            f'<div class="or-field or-field-{type(self).__name__}{inline}" data-field="{name}"'
            f"{wrapper_attrs}>{body}</div>"
        )

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        rel = self.get_relationship()
        d.update({
            "required": self._required if not callable(self._required) else None,
            "rules": [r if isinstance(r, str) else getattr(r, "__name__", "callable") for r in self._rules],
            "placeholder": self._placeholder if not callable(self._placeholder) else None,
            "input_type": self._input_type,
            "multiple": self._multiple,
            "searchable": self._searchable,
            "relationship": (
                (rel["name"], rel["title_attribute"]) if rel and set(rel.keys()) <= {
                    "name", "title_attribute", "search_columns", "preload", "modify_query", "get_option_label",
                } and not rel.get("search_columns") and not rel.get("preload")
                and rel.get("modify_query") is None and rel.get("get_option_label") is None
                else rel
            ),
            "options": self.get_options() if not callable(self._options) else {},
            "readonly": self._readonly,
            "validation_attribute": (
                self._validation_attribute if not callable(self._validation_attribute) else None
            ),
            "prefix": self._prefix if not callable(self._prefix) else None,
            "suffix": self._suffix if not callable(self._suffix) else None,
            "autofocus": self._autofocus,
        })
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        placeholder = self.get_placeholder(**ctx)
        ph = f' placeholder="{e(placeholder)}"' if placeholder else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        readonly = " readonly" if self._readonly else ""
        val = "" if state is None else e(str(state))
        wire = self._wire_binding(name)
        control = (
            f'<input class="or-input" id="or-{name}" name="{name}" type="{e(self._input_type)}" '
            f'value="{val}"{ph}{disabled}{readonly}{self._common_input_attrs(**ctx)}'
            f'{wire}{self._after_state_attr()} />'
        )
        return self.wrap_field(name, control, **ctx)


class TextInput(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._revealable = False
        self._copyable = False
        self._mask: str | None = None
        self._datalist: list[str] = []

    def revealable(self, condition: bool = True) -> Self:
        self._revealable = condition
        return self

    def copyable(self, condition: bool = True) -> Self:
        self._copyable = condition
        return self

    def mask(self, pattern: str) -> Self:
        self._mask = pattern
        return self

    def datalist(self, options: Sequence[str]) -> Self:
        self._datalist = list(options)
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        placeholder = self.get_placeholder(**ctx)
        ph = f' placeholder="{e(placeholder)}"' if placeholder else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        readonly = " readonly" if self._readonly else ""
        val = "" if state is None else e(str(state))
        wire = self._wire_binding(name)
        mask = f' data-mask="{e(self._mask)}"' if self._mask else ""
        list_attr = f' list="or-{name}-list"' if self._datalist else ""
        control = (
            f'<input class="or-input" id="or-{name}" name="{name}" type="{e(self._input_type)}" '
            f'value="{val}"{ph}{disabled}{readonly}{mask}{list_attr}'
            f'{self._common_input_attrs(**ctx)}{wire}{self._after_state_attr()} />'
        )
        if self._datalist:
            opts = "".join(f'<option value="{e(o)}"></option>' for o in self._datalist)
            control += f'<datalist id="or-{name}-list">{opts}</datalist>'
        extras = []
        if self._revealable and self._input_type == "password":
            extras.append(
                '<button type="button" class="or-btn or-btn-gray or-btn-sm" data-reveal '
                '@click="$refs.input.type = $refs.input.type === \'password\' ? \'text\' : \'password\'">'
                "Reveal</button>"
            )
            control = control.replace(f'id="or-{name}"', f'id="or-{name}" x-ref="input"', 1)
        if self._copyable:
            extras.append(
                '<button type="button" class="or-btn or-btn-gray or-btn-sm" data-copy '
                '@click="navigator.clipboard.writeText($refs.input.value)">Copy</button>'
            )
            if 'x-ref="input"' not in control:
                control = control.replace(f'id="or-{name}"', f'id="or-{name}" x-ref="input"', 1)
        if extras:
            control = f'<div class="or-input-actions">{control}{"".join(extras)}</div>'
        return self.wrap_field(name, control, **ctx)


class Textarea(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._autosize = False
        self._cols: int | None = None

    def autosize(self, condition: bool = True) -> Self:
        self._autosize = condition
        return self

    def cols(self, count: int) -> Self:
        self._cols = count
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        rows = self._rows or 4
        cols = f' cols="{self._cols}"' if self._cols else ""
        val = "" if state is None else e(str(state))
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        readonly = " readonly" if self._readonly else ""
        wire = self._wire_binding(name)
        autosize = ' data-autosize="true"' if self._autosize else ""
        control = (
            f'<textarea class="or-textarea" id="or-{name}" name="{name}" rows="{rows}"{cols}'
            f'{disabled}{readonly}{autosize}{self._common_input_attrs(**ctx)}'
            f'{wire}{self._after_state_attr()}>{val}</textarea>'
        )
        return self.wrap_field(name, control, **ctx)


class Select(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._create_option_form: Any = None
        self._edit_option_action: str | bool | None = None
        self._native = True
        self._options_limit: int | None = None
        self._allow_html = False
        self._search_prompt: str | None = None
        self._no_search_results_message: str | None = None
        self._loading_message: str | None = None
        self._searching_message: str | None = None
        self._search_debounce: int | None = None
        self._get_search_results_using: Callable[..., Any] | None = None
        self._get_option_label_using: Callable[..., Any] | None = None
        self._create_option_using: Callable[..., Any] | None = None
        self._min_items: int | None = None
        self._max_items: int | None = None
        self._reorderable_selected = False
        self._selectable_placeholder = True

    def create_option_form(self, form: Any) -> Self:
        self._create_option_form = form
        return self

    def edit_option_action(self, action: str | bool = True) -> Self:
        self._edit_option_action = action
        return self

    def native(self, condition: bool = True) -> Self:
        self._native = condition
        return self

    def options_limit(self, count: int) -> Self:
        self._options_limit = count
        return self

    def allow_html(self, condition: bool = True) -> Self:
        self._allow_html = condition
        return self

    def search_prompt(self, text: str) -> Self:
        self._search_prompt = text
        return self

    def no_search_results_message(self, text: str) -> Self:
        self._no_search_results_message = text
        return self

    def loading_message(self, text: str) -> Self:
        self._loading_message = text
        return self

    def searching_message(self, text: str) -> Self:
        self._searching_message = text
        return self

    def search_debounce(self, ms: int) -> Self:
        self._search_debounce = ms
        return self

    def get_search_results_using(self, callback: Callable[..., Any]) -> Self:
        self._get_search_results_using = callback
        return self

    def get_option_label_using(self, callback: Callable[..., Any]) -> Self:
        self._get_option_label_using = callback
        return self

    def create_option_using(self, callback: Callable[..., Any]) -> Self:
        self._create_option_using = callback
        return self

    def min_items(self, count: int) -> Self:
        self._min_items = count
        return self

    def max_items(self, count: int) -> Self:
        self._max_items = count
        return self

    def reorderable(self, condition: bool = True) -> Self:
        self._reorderable_selected = condition
        return self

    def selectable_placeholder(self, condition: bool = True) -> Self:
        self._selectable_placeholder = condition
        return self

    def _render_options_html(self, state: Any, **ctx: Any) -> str:
        selected = state if isinstance(state, (list, tuple, set)) else ([state] if state not in (None, "") else [])
        selected_s = {str(s) for s in selected}
        chunks: list[str] = []
        count = 0
        for group_label, opts in self.get_option_groups(**ctx):
            inner = []
            for k, v in opts.items():
                if self._options_limit is not None and count >= self._options_limit:
                    break
                sel = " selected" if str(k) in selected_s else ""
                label = str(v) if self._allow_html else e(v)
                inner.append(
                    f'<option value="{e(k)}" data-label="{e(v)}"{sel}>{label}</option>'
                )
                count += 1
            body = "".join(inner)
            if group_label:
                chunks.append(f'<optgroup label="{e(group_label)}">{body}</optgroup>')
            else:
                chunks.append(body)
        return "".join(chunks)

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        opts_html = self._render_options_html(state, **ctx)
        multi = " multiple" if self._multiple else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        wire = self._wire_binding(name)
        searchable = self._searchable or not self._native
        searchable_attr = " data-searchable" if searchable else ""
        alpine = ' x-data="orbitSearchableSelect"' if searchable else ""
        search_input = ""
        if searchable:
            prompt = e(self._search_prompt or "Search…")
            search_input = (
                f'<input type="search" class="or-input or-select-search" placeholder="{prompt}" '
                f'x-model="q" x-on:input.debounce.{self._search_debounce or 200}ms="filter()" '
                f'aria-label="Search" />'
            )
        select_ref = ' x-ref="select"' if searchable else ""
        actions = []
        if self._create_option_form is not None or self._create_option_using is not None:
            actions.append(
                f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
                f'data-create-option wire:click="mountCreateOption(\'{name}\')">Create option</button>'
            )
        if self._edit_option_action:
            action_name = (
                self._edit_option_action if isinstance(self._edit_option_action, str) else "editOption"
            )
            actions.append(
                f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
                f'data-edit-option wire:click="mountAction(\'{e(action_name)}\')">Edit option</button>'
            )
        actions_html = f'<div class="or-select-actions">{"".join(actions)}</div>' if actions else ""
        rel = self.get_relationship()
        rel_attrs = ""
        if rel:
            rel_attrs = f' data-relationship="{e(rel["name"])}"'
            if rel.get("search_columns"):
                rel_attrs += f' data-search-columns="{e(",".join(rel["search_columns"]))}"'
            if rel.get("preload"):
                rel_attrs += ' data-preload="true"'
        if self._get_search_results_using is not None:
            rel_attrs += ' data-ajax-search="true"'
        if self._no_search_results_message:
            rel_attrs += f' data-no-results="{e(self._no_search_results_message)}"'
        if self._loading_message:
            rel_attrs += f' data-loading="{e(self._loading_message)}"'
        if self._searching_message:
            rel_attrs += f' data-searching="{e(self._searching_message)}"'
        if self._min_items is not None:
            rel_attrs += f' data-min-items="{self._min_items}"'
        if self._max_items is not None:
            rel_attrs += f' data-max-items="{self._max_items}"'
        if self._reorderable_selected:
            rel_attrs += ' data-reorderable="true"'
        if not self._native:
            rel_attrs += ' data-native="false"'
        placeholder_opt = ""
        if self._selectable_placeholder and not self._multiple:
            placeholder_opt = '<option value="">—</option>'
        control = (
            f"{search_input}"
            f'<select class="or-select" id="or-{name}" name="{name}"{multi}{disabled}'
            f'{select_ref}{wire}{self._after_state_attr()}>{placeholder_opt}{opts_html}</select>'
            f"{actions_html}"
        )
        # wrap_field adds outer div — inject searchable attrs onto wrapper via extra
        html = self.wrap_field(name, control, **ctx)
        inject = f'data-field="{name}"{searchable_attr}{rel_attrs}{alpine}'
        return html.replace(f'data-field="{name}"', inject, 1)


class Checkbox(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        checked = " checked" if state else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        return (
            f'<div class="or-field or-field-Checkbox" data-field="{name}">'
            f'<label class="or-checkbox-label"><input class="or-checkbox" type="checkbox" '
            f'name="{name}"{self._wire_binding(name)}{checked}{disabled} /> {label}</label></div>'
        )


class Toggle(Checkbox):
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        return html.replace("or-field-Checkbox", "or-field-Toggle").replace("or-checkbox", "or-toggle")


class Hidden(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        name = e(self.get_state_path() or "")
        val = "" if state is None else e(str(state))
        return f'<input type="hidden" name="{name}" value="{val}"{self._wire_binding(name)} />'


class Placeholder(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._content: str = ""
        self._dehydrated = False

    def content(self, text: str) -> Self:
        self._content = text
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        return (
            f'<div class="or-placeholder"><p class="or-placeholder-content">'
            f'{e(self._content or state or "")}</p></div>'
        )


class DatePicker(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "date"
        self._min_date: str | None = None
        self._max_date: str | None = None
        self._display_format: str | None = None
        self._native = True

    def min_date(self, value: str) -> Self:
        self._min_date = value
        return self

    def max_date(self, value: str) -> Self:
        self._max_date = value
        return self

    def display_format(self, fmt: str) -> Self:
        self._display_format = fmt
        return self

    def native(self, condition: bool = True) -> Self:
        self._native = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        placeholder = self.get_placeholder(**ctx)
        ph = f' placeholder="{e(placeholder)}"' if placeholder else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        readonly = " readonly" if self._readonly else ""
        val = "" if state is None else e(str(state))
        attrs = []
        if self._min_date:
            attrs.append(f'min="{e(self._min_date)}"')
        if self._max_date:
            attrs.append(f'max="{e(self._max_date)}"')
        if self._display_format:
            attrs.append(f'data-display-format="{e(self._display_format)}"')
        if not self._native:
            attrs.append('data-native="false"')
        attr_s = (" " + " ".join(attrs)) if attrs else ""
        control = (
            f'<input class="or-input" id="or-{name}" name="{name}" type="{e(self._input_type)}" '
            f'value="{val}"{ph}{disabled}{readonly}{attr_s}{self._common_input_attrs(**ctx)}'
            f'{self._wire_binding(name)}{self._after_state_attr()} />'
        )
        return self.wrap_field(name, control, **ctx)


class DateTimePicker(DatePicker):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "datetime-local"


class TimePicker(DatePicker):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "time"


class FileUpload(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._disk: str | None = None
        self._directory: str | None = None
        self._avatar = False
        self._image_preview = False
        self._reorderable = False
        self._min_size: int | None = None
        self._image_min_width: int | None = None
        self._image_max_width: int | None = None
        self._image_min_height: int | None = None
        self._image_max_height: int | None = None
        self._visibility: str | None = None
        self._downloadable = False
        self._openable = False
        self._previewable = True
        self._move_files = False
        self._store_files = True
        self._fetch_file_information = True
        self._preserve_filenames = False
        self._image_editor = False
        self._image_editor_aspect_ratios: list[str] = []
        self._max_files: int | None = None
        self._min_files: int | None = None
        self._panel_layout = False
        self._image_preview_height: int | None = None
        self._prevent_file_path_tampering = False

    def disk(self, name: str) -> Self:
        self._disk = name
        return self

    def directory(self, path: str) -> Self:
        self._directory = path
        return self

    def visibility(self, value: str) -> Self:
        self._visibility = value
        return self

    def downloadable(self, condition: bool = True) -> Self:
        self._downloadable = condition
        return self

    def openable(self, condition: bool = True) -> Self:
        self._openable = condition
        return self

    def previewable(self, condition: bool = True) -> Self:
        self._previewable = condition
        return self

    def move_files(self, condition: bool = True) -> Self:
        self._move_files = condition
        return self

    def store_files(self, condition: bool = True) -> Self:
        self._store_files = condition
        return self

    def fetch_file_information(self, condition: bool = True) -> Self:
        self._fetch_file_information = condition
        return self

    def preserve_filenames(self, condition: bool = True) -> Self:
        self._preserve_filenames = condition
        return self

    def image_editor(self, condition: bool = True) -> Self:
        self._image_editor = condition
        return self

    def image_editor_aspect_ratios(self, ratios: Sequence[str]) -> Self:
        self._image_editor_aspect_ratios = list(ratios)
        self._image_editor = True
        return self

    def max_files(self, count: int) -> Self:
        self._max_files = count
        return self

    def min_files(self, count: int) -> Self:
        self._min_files = count
        return self

    def panel_layout(self, condition: bool = True) -> Self:
        self._panel_layout = condition
        return self

    def image_preview_height(self, px: int) -> Self:
        self._image_preview_height = px
        return self

    def prevent_file_path_tampering(self, condition: bool = True) -> Self:
        self._prevent_file_path_tampering = condition
        return self

    def avatar(self, condition: bool = True) -> Self:
        self._avatar = condition
        if condition:
            self._image_preview = True
            if not self._accepted_file_types:
                self._accepted_file_types = ["image/*"]
        return self

    def image_preview(self, condition: bool = True) -> Self:
        self._image_preview = condition
        return self

    def reorderable(self, condition: bool = True) -> Self:
        self._reorderable = condition
        return self

    def image(self) -> Self:
        self._accepted_file_types = ["image/png", "image/jpeg", "image/gif", "image/webp"]
        self._image_preview = True
        return self

    def accepted_images(self) -> Self:
        return self.image()

    def min_size(self, kilobytes: int) -> Self:
        self._min_size = kilobytes
        return self

    def image_size(
        self,
        *,
        min_width: int | None = None,
        max_width: int | None = None,
        min_height: int | None = None,
        max_height: int | None = None,
    ) -> Self:
        self._image_min_width = min_width
        self._image_max_width = max_width
        self._image_min_height = min_height
        self._image_max_height = max_height
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        accept = ",".join(self._accepted_file_types)
        acc = f' accept="{e(accept)}"' if accept else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        multi = " multiple" if self._multiple or (self._max_files or 0) > 1 else ""
        attrs = []
        if self._disk:
            attrs.append(f'data-disk="{e(self._disk)}"')
        if self._directory:
            attrs.append(f'data-directory="{e(self._directory)}"')
        if self._visibility:
            attrs.append(f'data-visibility="{e(self._visibility)}"')
        if self._avatar:
            attrs.append('data-avatar="true"')
        if self._image_preview and self._previewable:
            attrs.append('data-image-preview="true"')
        if self._reorderable:
            attrs.append('data-reorderable="true"')
        if self._downloadable:
            attrs.append('data-downloadable="true"')
        if self._openable:
            attrs.append('data-openable="true"')
        if self._move_files:
            attrs.append('data-move-files="true"')
        if not self._store_files:
            attrs.append('data-store-files="false"')
        if not self._fetch_file_information:
            attrs.append('data-fetch-file-information="false"')
        if self._preserve_filenames:
            attrs.append('data-preserve-filenames="true"')
        if self._image_editor:
            attrs.append('data-image-editor="true"')
        if self._image_editor_aspect_ratios:
            attrs.append(f'data-aspect-ratios="{e(",".join(self._image_editor_aspect_ratios))}"')
        if self._max_size is not None:
            attrs.append(f'data-max-size="{self._max_size}"')
        if self._min_size is not None:
            attrs.append(f'data-min-size="{self._min_size}"')
        if self._max_files is not None:
            attrs.append(f'data-max-files="{self._max_files}"')
        if self._min_files is not None:
            attrs.append(f'data-min-files="{self._min_files}"')
        if self._panel_layout:
            attrs.append('data-panel-layout="true"')
        if self._image_preview_height is not None:
            attrs.append(f'data-preview-height="{self._image_preview_height}"')
        if self._prevent_file_path_tampering:
            attrs.append('data-prevent-tampering="true"')
        for key, val in (
            ("min-width", self._image_min_width),
            ("max-width", self._image_max_width),
            ("min-height", self._image_min_height),
            ("max-height", self._image_max_height),
        ):
            if val is not None:
                attrs.append(f'data-image-{key}="{val}"')
        attr_str = (" " + " ".join(attrs)) if attrs else ""
        avatar_cls = " or-file-avatar" if self._avatar else ""
        preview = ""
        if self._image_preview and self._previewable:
            preview = '<div class="or-file-preview" data-preview-grid aria-live="polite"></div>'
        editor = ""
        if self._image_editor:
            editor = '<div class="or-file-image-editor" data-image-editor-ui hidden></div>'
        control = (
            f"{preview}{editor}"
            f'<input class="or-file" id="or-{name}" type="file" name="{name}"{acc}{multi}{disabled} '
            f'{self._wire_binding(name)} />'
        )
        html = self.wrap_field(name, control, **ctx)
        return html.replace(
            'class="or-field or-field-FileUpload"',
            f'class="or-field or-field-FileUpload{avatar_cls}"',
            1,
        ).replace(f'data-field="{name}"', f'data-field="{name}"{attr_str}', 1)


class Radio(Select):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        opts = []
        for k, v in self.get_options(**ctx).items():
            checked = " checked" if str(k) == str(state) else ""
            desc = self._option_descriptions.get(str(k))
            desc_html = f'<span class="or-option-desc">{e(desc)}</span>' if desc else ""
            opts.append(
                f'<label class="or-radio-label"><input type="radio" class="or-radio" '
                f'name="{name}" value="{e(k)}" wire:model="{name}"{checked}{disabled} /> '
                f'<span class="or-option-body"><span class="or-option-label">{e(v)}</span>{desc_html}</span></label>'
            )
        cols = f' style="--or-options-cols:{self._options_columns}"' if self._options_columns else ""
        cols_cls = f" or-options-cols-{self._options_columns}" if self._options_columns else ""
        return (
            f'<div class="or-field or-field-Radio{cols_cls}" data-field="{name}" role="radiogroup" '
            f'aria-label="{label}"{cols}><span class="or-label">{label}</span>'
            f'<div class="or-options">{"".join(opts)}</div></div>'
        )


class CheckboxList(Select):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._multiple = True
        self._bulk_toggle = False

    def bulk_toggleable(self, condition: bool = True) -> Self:
        self._bulk_toggle = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        selected = state if isinstance(state, (list, tuple, set)) else ([state] if state not in (None, "") else [])
        selected_s = {str(s) for s in selected}
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        opts = []
        for k, v in self.get_options(**ctx).items():
            checked = " checked" if str(k) in selected_s else ""
            desc = self._option_descriptions.get(str(k))
            desc_html = f'<span class="or-option-desc">{e(desc)}</span>' if desc else ""
            opts.append(
                f'<label class="or-checkbox-label"><input type="checkbox" class="or-checkbox" '
                f'name="{name}" value="{e(k)}" wire:model="{name}"{checked}{disabled} /> '
                f'<span class="or-option-body"><span class="or-option-label">{e(v)}</span>{desc_html}</span></label>'
            )
        bulk = ""
        if self._bulk_toggle:
            bulk = (
                '<div class="or-checkbox-list-bulk">'
                '<button type="button" class="or-link-btn" data-select-all>Select all</button>'
                '<button type="button" class="or-link-btn" data-deselect-all>Deselect all</button>'
                "</div>"
            )
        cols = f' style="--or-options-cols:{self._options_columns}"' if self._options_columns else ""
        cols_cls = f" or-options-cols-{self._options_columns}" if self._options_columns else ""
        return (
            f'<div class="or-field or-field-CheckboxList{cols_cls}" data-field="{name}"{cols}>'
            f'<span class="or-label">{label}</span>{bulk}'
            f'<div class="or-checkbox-list">{"".join(opts)}</div></div>'
        )


class TagsInput(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._suggestions: list[str] = []
        self._separator: str = ","
        self._reorderable = False

    def suggestions(self, items: Sequence[str]) -> Self:
        self._suggestions = list(items)
        return self

    def separator(self, value: str) -> Self:
        self._separator = value
        return self

    def reorderable(self, condition: bool = True) -> Self:
        self._reorderable = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        tags = state if isinstance(state, (list, tuple)) else (
            [t.strip() for t in str(state).split(self._separator) if t.strip()] if state else []
        )
        chips = "".join(f'<span class="or-tag">{e(t)}</span>' for t in tags)
        val = e(self._separator.join(str(t) for t in tags))
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        suggestions = ""
        if self._suggestions:
            opts = "".join(f'<option value="{e(s)}"></option>' for s in self._suggestions)
            suggestions = f'<datalist id="or-{name}-suggestions">{opts}</datalist>'
            list_attr = f' list="or-{name}-suggestions"'
        else:
            list_attr = ""
        reorder = ' data-reorderable="true"' if self._reorderable else ""
        return (
            f'<div class="or-field or-field-TagsInput" data-field="{name}" '
            f'data-separator="{e(self._separator)}"{reorder} x-data="{{ tags: \'{val}\' }}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<div class="or-tags">{chips}'
            f'<input class="or-input or-tags-input" id="or-{name}" name="{name}" value="{val}"'
            f'{disabled}{list_attr} wire:model="{name}" placeholder="Add tag…" /></div>'
            f"{suggestions}</div>"
        )


class ColorPicker(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "color"


class MoneyInput(TextInput):
    """Currency amount input with prefix/suffix chrome (Filament ``MoneyInput``-style)."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "number"
        self._currency = "USD"
        self._locale: str | None = None
        self.step("0.01")
        self.input_mode("decimal")
        self.prefix("$")

    def currency(self, code: str) -> Self:
        self._currency = code
        symbols = {"USD": "$", "EUR": "€", "GBP": "£", "KES": "KSh"}
        self.prefix(symbols.get(code.upper(), code.upper() + " "))
        return self

    def locale(self, value: str) -> Self:
        self._locale = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        extra = f' data-currency="{e(self._currency)}"'
        if self._locale:
            extra += f' data-locale="{e(self._locale)}"'
        return html.replace(
            'class="or-field or-field-TextInput"',
            f'class="or-field or-field-MoneyInput"{extra}',
            1,
        )


class RichEditor(Textarea):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._toolbar_buttons: list[str] = ["bold", "italic", "link"]

    def toolbar_buttons(self, buttons: Sequence[str]) -> Self:
        self._toolbar_buttons = list(buttons)
        return self

    def get_toolbar_buttons(self) -> list[str]:
        return list(self._toolbar_buttons)

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        val = "" if state is None else str(state)
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        live = " wire:model.live" if self._live else " wire:model"
        toolbar = ",".join(self._toolbar_buttons)
        toolbar_spans = "".join(
            f'<button type="button" class="or-editor-tool" data-tool="{e(b)}" '
            f'aria-label="{e(b)}">{e(b[:1].upper() + b[1:])}</button>'
            for b in self._toolbar_buttons
        )
        return (
            f'<div class="or-field or-field-RichEditor" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<div class="or-editor-toolbar" data-toolbar="{e(toolbar)}">{toolbar_spans}</div>'
            f'<div class="or-editor or-editor-rich" id="or-{name}-editor" data-tiptap '
            f'data-toolbar="{e(toolbar)}" data-input="or-{name}"{disabled}></div>'
            f'<input type="hidden" class="or-editor-input" id="or-{name}" name="{name}" '
            f'value="{e(val)}"{live}="{name}" data-tiptap-input /></div>'
        )


class MarkdownEditor(Textarea):
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        return html.replace("or-field-Textarea", "or-field-MarkdownEditor").replace(
            "or-textarea", "or-textarea or-editor or-editor-markdown"
        )


class KeyValue(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        data = state if isinstance(state, dict) else {}
        rows = []
        for i, (k, v) in enumerate(data.items()):
            rows.append(
                f'<div class="or-key-value-row" data-index="{i}">'
                f'<input class="or-input" name="{name}_key_{i}" value="{e(k)}" placeholder="Key" />'
                f'<input class="or-input" name="{name}_val_{i}" value="{e(v)}" placeholder="Value" '
                f'wire:model="{name}.{e(k)}" /></div>'
            )
        if not rows:
            rows.append(
                '<div class="or-key-value-row">'
                '<input class="or-input" placeholder="Key" /><input class="or-input" placeholder="Value" /></div>'
            )
        return (
            f'<div class="or-field or-field-KeyValue" data-field="{name}">'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-key-value-editor">{"".join(rows)}</div>'
            f'<button type="button" class="or-btn or-btn-gray or-btn-sm" wire:click="addKeyValueRow(\'{name}\')">'
            f"Add row</button></div>"
        )


class Repeater(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._schema: list[Component] = []
        self._cloneable = False
        self._collapsible = False
        self._reorderable_items = False
        self._item_label: str | Callable[..., str] | None = None
        self._min_items: int | None = None
        self._max_items: int | None = None
        self._default_items: int = 1
        self._addable = True
        self._deletable = True
        self._add_action_label: str = "Add item"
        self._simple_field: Component | None = None
        self._grid_columns: int | None = None
        self._table_columns: list[str] = []
        self._relationship_name: str | None = None
        self._mutate_relationship_data_before_create: Callable[..., Any] | None = None
        self._mutate_relationship_data_before_fill: Callable[..., Any] | None = None
        self._mutate_relationship_data_before_save: Callable[..., Any] | None = None

    def schema(self, components: Sequence[Component]) -> Self:
        self._schema = list(components)
        return self

    def get_schema(self) -> list[Component]:
        if self._simple_field is not None:
            return [self._simple_field]
        return list(self._schema)

    def simple(self, field: Component) -> Self:
        self._simple_field = field
        return self

    def default_items(self, count: int) -> Self:
        self._default_items = count
        return self

    def addable(self, condition: bool = True) -> Self:
        self._addable = condition
        return self

    def deletable(self, condition: bool = True) -> Self:
        self._deletable = condition
        return self

    def add_action_label(self, label: str) -> Self:
        self._add_action_label = label
        return self

    def grid(self, columns: int) -> Self:
        self._grid_columns = columns
        return self

    def table(self, columns: Sequence[str]) -> Self:
        self._table_columns = list(columns)
        return self

    def relationship(self, name: str | None = None) -> Self:  # type: ignore[override]
        self._relationship_name = name or self.get_name()
        return self

    def mutate_relationship_data_before_create(self, callback: Callable[..., Any]) -> Self:
        self._mutate_relationship_data_before_create = callback
        return self

    def mutate_relationship_data_before_fill(self, callback: Callable[..., Any]) -> Self:
        self._mutate_relationship_data_before_fill = callback
        return self

    def mutate_relationship_data_before_save(self, callback: Callable[..., Any]) -> Self:
        self._mutate_relationship_data_before_save = callback
        return self

    def apply_mutate_before_create(self, data: Any, **ctx: Any) -> Any:
        if self._mutate_relationship_data_before_create is None:
            return data
        return evaluate(self._mutate_relationship_data_before_create, data, **ctx)

    def apply_mutate_before_fill(self, data: Any, **ctx: Any) -> Any:
        if self._mutate_relationship_data_before_fill is None:
            return data
        return evaluate(self._mutate_relationship_data_before_fill, data, **ctx)

    def apply_mutate_before_save(self, data: Any, **ctx: Any) -> Any:
        if self._mutate_relationship_data_before_save is None:
            return data
        return evaluate(self._mutate_relationship_data_before_save, data, **ctx)

    def cloneable(self, condition: bool = True) -> Self:
        self._cloneable = condition
        return self

    def collapsible(self, condition: bool = True) -> Self:
        self._collapsible = condition
        return self

    def reorderable(self, condition: bool = True) -> Self:
        self._reorderable_items = condition
        return self

    def item_label(self, label: str | Callable[..., str]) -> Self:
        self._item_label = label
        return self

    def min_items(self, count: int) -> Self:
        self._min_items = count
        return self

    def max_items(self, count: int) -> Self:
        self._max_items = count
        return self

    def get_item_label(self, index: int, item: Any, **ctx: Any) -> str:
        if self._item_label is None:
            return f"Item {index + 1}"
        result = evaluate(self._item_label, index=index, item=item, state=item, **ctx)
        return str(result)

    def _item_schema_for(self, item: Any) -> list[Component]:
        return self.get_schema()

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        items = state if isinstance(state, list) else None
        if items is None:
            items = [{} for _ in range(max(self._default_items, 0))] or [{}]
        if not items and self._default_items:
            items = [{} for _ in range(self._default_items)]
        if not items:
            items = [{}]
        blocks = []
        for index, item in enumerate(items):
            fields = []
            for child in self._item_schema_for(item):
                child_state = None
                if isinstance(item, dict):
                    child_state = item.get(child.get_state_path() or child.get_name())
                fields.append(child.render(child_state, **ctx, index=index, record=item))
            item_label = e(self.get_item_label(index, item, **ctx))
            controls = []
            if self._reorderable_items:
                controls.append(
                    f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
                    f'wire:click="moveRepeaterItem(\'{name}\', {index}, -1)" '
                    f'data-reorder="up" aria-label="Move up">↑</button>'
                )
                controls.append(
                    f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
                    f'wire:click="moveRepeaterItem(\'{name}\', {index}, 1)" '
                    f'data-reorder="down" aria-label="Move down">↓</button>'
                )
            if self._cloneable:
                controls.append(
                    f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
                    f'wire:click="cloneRepeaterItem(\'{name}\', {index})" data-clone>Clone</button>'
                )
            if self._collapsible:
                controls.append(
                    '<button type="button" class="or-btn or-btn-gray or-btn-sm" '
                    '@click="collapsed = !collapsed" data-collapse '
                    'x-text="collapsed ? \'Expand\' : \'Collapse\'">Collapse</button>'
                )
            if self._deletable:
                controls.append(
                    f'<button type="button" class="or-btn or-btn-danger or-btn-sm" '
                    f'wire:click="removeRepeaterItem(\'{name}\', {index})">Remove</button>'
                )
            collapse_data = ' x-data="{ collapsed: false }"' if self._collapsible else ""
            body_bind = ' x-show="!collapsed"' if self._collapsible else ""
            blocks.append(
                f'<div class="or-repeater-item" data-index="{index}"{collapse_data}>'
                f'<div class="or-repeater-item-header">'
                f'<span class="or-repeater-item-label">{item_label}</span>'
                f'<div class="or-repeater-item-actions">{"".join(controls)}</div></div>'
                f'<div class="or-repeater-item-body"{body_bind}>{"".join(fields)}</div></div>'
            )
        limits = []
        if self._min_items is not None:
            limits.append(f'data-min-items="{self._min_items}"')
        if self._max_items is not None:
            limits.append(f'data-max-items="{self._max_items}"')
        if self._grid_columns is not None:
            limits.append(f'data-grid="{self._grid_columns}"')
        if self._relationship_name:
            limits.append(f'data-relationship="{e(self._relationship_name)}"')
        if self._table_columns:
            limits.append(f'data-table-columns="{e(",".join(self._table_columns))}"')
        limit_attrs = (" " + " ".join(limits)) if limits else ""
        add_html = ""
        if self._addable:
            add_disabled = ""
            if self._max_items is not None and len(items) >= self._max_items:
                add_disabled = " disabled"
            add_html = (
                f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
                f'wire:click="addRepeaterItem(\'{name}\')"{add_disabled}>'
                f"{e(self._add_action_label)}</button>"
            )
        simple_cls = " or-repeater-simple" if self._simple_field else ""
        table_cls = " or-repeater-table" if self._table_columns else ""
        table_head = ""
        if self._table_columns:
            ths = "".join(f'<th class="or-repeater-th">{e(c)}</th>' for c in self._table_columns)
            table_head = f'<div class="or-repeater-table-head"><table><thead><tr>{ths}<th></th></tr></thead></table></div>'
        return (
            f'<div class="or-field or-field-Repeater{simple_cls}{table_cls}" data-field="{name}"{limit_attrs} '
            f'x-data="{{ items: {len(items)} }}">'
            f'<span class="or-label">{label}</span>{table_head}'
            f'<div class="or-repeater">{"".join(blocks)}</div>'
            f"{add_html}</div>"
        )


class Block(Component):
    """Builder block definition — ``Block.make("hero").label().icon().schema()``."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._schema: list[Component] = []
        self._icon: str | None = None
        self._max_items: int | None = None

    def schema(self, components: Sequence[Component]) -> Self:
        self._schema = list(components)
        return self

    def get_schema(self) -> list[Component]:
        return list(self._schema)

    def icon(self, name: str) -> Self:
        self._icon = name
        return self

    def max_items(self, count: int) -> Self:
        self._max_items = count
        return self

    def get_max_items(self) -> int | None:
        return self._max_items


class Builder(Repeater):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._blocks: list[Block] = []
        self._block_picker_columns: int | None = None

    def blocks(self, blocks: Sequence[Block]) -> Self:
        self._blocks = list(blocks)
        if blocks and not self._schema:
            self._schema = list(blocks[0].get_schema())
        return self

    def get_blocks(self) -> list[Block]:
        return list(self._blocks)

    def block_picker_columns(self, count: int) -> Self:
        self._block_picker_columns = count
        return self

    def _item_schema_for(self, item: Any) -> list[Component]:
        if isinstance(item, dict) and self._blocks:
            btype = str(item.get("type") or item.get("block") or "")
            for block in self._blocks:
                if (block.get_name() or "") == btype:
                    return block.get_schema()
        return self.get_schema()

    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx).replace("or-field-Repeater", "or-field-Builder")
        if not self._blocks:
            return html
        items = state if isinstance(state, list) else [{}]
        counts: dict[str, int] = {}
        for item in items:
            if isinstance(item, dict):
                t = str(item.get("type") or item.get("block") or "")
                if t:
                    counts[t] = counts.get(t, 0) + 1
        name = e(self.get_state_path() or "")
        picker_btns = []
        for block in self._blocks:
            bname = block.get_name() or "block"
            blabel = e(block.get_label(**ctx) or bname)
            icon = f' data-icon="{e(block._icon)}"' if block._icon else ""
            disabled = ""
            max_i = block.get_max_items()
            if max_i is not None and counts.get(bname, 0) >= max_i:
                disabled = " disabled"
            max_attr = f' data-max-items="{max_i}"' if max_i is not None else ""
            picker_btns.append(
                f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
                f'data-block="{e(bname)}"{icon}{max_attr}{disabled} '
                f'wire:click="addBuilderBlock(\'{name}\', \'{e(bname)}\')">{blabel}</button>'
            )
        cols = (
            f' style="grid-template-columns:repeat({self._block_picker_columns},minmax(0,1fr))"'
            if self._block_picker_columns
            else ""
        )
        picker = f'<div class="or-builder-picker" role="group"{cols}>{"".join(picker_btns)}</div>'
        # Replace add button with picker
        add_marker = f'wire:click="addRepeaterItem(\'{name}\')"'
        idx = html.find(add_marker)
        if idx >= 0:
            start = html.rfind("<button", 0, idx)
            end = html.find("</button>", idx) + len("</button>")
            if start >= 0:
                html = html[:start] + picker + html[end:]
            else:
                html = html.replace("</div>", picker + "</div>", 1) if False else html + picker
        elif html.endswith("</div>"):
            html = html[:-6] + picker + "</div>"
        return html


class Slider(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "range"
        self._min_value = 0
        self._max_value = 100
        self._step = 1
        self._pips = False

    def pips(self, condition: bool = True) -> Self:
        self._pips = condition
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        if self._pips:
            html = html.replace("or-input", "or-input or-slider", 1).replace(
                'type="range"', 'type="range" data-pips="true"', 1
            )
        else:
            html = html.replace("or-input", "or-input or-slider", 1)
        return html


class ToggleButtons(Select):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        buttons = []
        for k, v in self.get_options(**ctx).items():
            active = " is-active" if str(k) == str(state) else ""
            checked = " checked" if str(k) == str(state) else ""
            buttons.append(
                f'<label class="or-toggle-btn{active}">'
                f'<input type="radio" name="{name}" value="{e(k)}" {self.wire_model_directive()}="{name}"'
                f'{checked}{disabled} class="or-sr-only" />'
                f"<span>{e(v)}</span></label>"
            )
        return (
            f'<div class="or-field or-field-ToggleButtons" data-field="{name}">'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-toggle-buttons" role="group">{"".join(buttons)}</div></div>'
        )


class CodeEditor(Textarea):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._language: str | None = None

    def language(self, lang: str) -> Self:
        self._language = lang
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        html = html.replace("or-field-Textarea", "or-field-CodeEditor").replace(
            "or-textarea", "or-textarea or-editor or-editor-code"
        )
        if self._language:
            html = html.replace(
                'class="or-textarea or-editor or-editor-code"',
                f'class="or-textarea or-editor or-editor-code" data-language="{e(self._language)}"',
                1,
            )
        return html


class RelationshipRepeater(Repeater):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if self._relationship_name is None:
            self._relationship_name = self.get_name()
        return super().render(state, **ctx).replace("or-field-Repeater", "or-field-RelationshipRepeater")


class MultiSelect(Select):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._multiple = True


class OneTimeCodeInput(TextInput):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "text"
        self._autocomplete = "one-time-code"


class ViewField(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._dehydrated = False
        self._view_html: str | Callable[..., str] | None = None

    def content(self, html: str | Callable[..., str]) -> Self:
        self._view_html = html
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        body = evaluate(self._view_html, state=state, **ctx) if self._view_html else e("" if state is None else str(state))
        return (
            f'<div class="or-field or-field-ViewField" data-field="{name}">'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-view-field">{body}</div></div>'
        )


class MorphToSelect(Select):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._types: list[Any] = []
        self._type_field: str = "type"
        self._id_field: str = "id"

    def types(self, types: Sequence[Any]) -> Self:
        """Accept ``['App\\\\Models\\\\User', …]`` or ``[{'type': …, 'label': …, 'options': …}]``."""
        self._types = list(types)
        return self

    def type_attribute(self, name: str) -> Self:
        self._type_field = name
        return self

    def id_attribute(self, name: str) -> Self:
        self._id_field = name
        return self

    def get_types(self) -> list[Any]:
        return list(self._types)

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        live = " wire:model.live" if self._live else " wire:model"

        type_value = None
        id_value = state
        if isinstance(state, dict):
            type_value = state.get(self._type_field) or state.get("type")
            id_value = state.get(self._id_field) or state.get("id")
        elif isinstance(state, str) and ":" in state:
            type_value, id_value = state.split(":", 1)

        type_options = []
        id_options_by_type: dict[str, dict[Any, Any]] = {}
        for t in self._types:
            if isinstance(t, Mapping):
                key = str(t.get("type") or t.get("value") or t.get("name") or "")
                tlabel = t.get("label") or key
                type_options.append((key, tlabel))
                if t.get("options"):
                    id_options_by_type[key] = dict(t["options"])
            else:
                type_options.append((str(t), str(t).rsplit("\\", 1)[-1]))

        if not type_options and self._options:
            # Fall back to flat options as morph keys.
            for k, v in self.get_options(**ctx).items():
                type_options.append((str(k), v))

        type_name = e(f"{name}_{self._type_field}" if not name.endswith(self._type_field) else name)
        type_opts_html = []
        for k, v in type_options:
            sel = " selected" if type_value is not None and str(k) == str(type_value) else ""
            type_opts_html.append(f'<option value="{e(k)}"{sel}>{e(v)}</option>')

        # ID select: use type-specific options or inherited options.
        id_opts = id_options_by_type.get(str(type_value or ""), {})
        if not id_opts:
            id_opts = self.get_options(**ctx)
        id_opts_html = []
        for k, v in id_opts.items():
            sel = " selected" if id_value is not None and str(k) == str(id_value) else ""
            id_opts_html.append(f'<option value="{e(k)}"{sel}>{e(v)}</option>')

        searchable_attr = " data-searchable" if self._searchable else ""
        return (
            f'<div class="or-field or-field-MorphToSelect" data-field="{name}"{searchable_attr} '
            f'x-data="orbitMorphToSelect">'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-morph-to-select">'
            f'<select class="or-select or-select-morph or-select-morph-type" '
            f'name="{type_name}" data-morph-type{disabled}{live}="{type_name}">'
            f'{"".join(type_opts_html)}</select>'
            f'<select class="or-select or-select-morph or-select-morph-id" '
            f'name="{e(name)}" data-morph-id{disabled}{live}="{name}">'
            f'{"".join(id_opts_html)}</select>'
            f"</div></div>"
        )


class TableSelect(Select):
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        return html.replace("or-field-Select", "or-field-TableSelect").replace(
            'class="or-select"', 'class="or-select or-select-table"', 1
        )


class ModalTableSelect(Select):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        display = "" if state is None else e(str(state))
        return (
            f'<div class="or-field or-field-ModalTableSelect" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<div class="or-modal-table-select">'
            f'<input class="or-input" id="or-{name}" name="{name}" value="{display}" '
            f'readonly wire:model="{name}" />'
            f'<button type="button" class="or-btn or-btn-gray" '
            f'wire:click="mountTableSelect(\'{name}\')">Browse</button></div></div>'
        )
