"""Form fields — Filament-familiar fluent API."""

from __future__ import annotations

import json
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


def _normalize_string_list(state: Any, *, separator: str = ",") -> list[str]:
    """Normalize TagsInput / CheckboxList state to a list of strings.

    Handles real lists, comma-separated text, and JSON array strings (common when
    ORM ``array`` casts leak raw storage into form state).
    """
    if isinstance(state, (list, tuple, set)):
        return [str(t).strip() for t in state if str(t).strip()]
    if state in (None, ""):
        return []
    if isinstance(state, str):
        text = state.strip()
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, list):
                return [str(t).strip() for t in parsed if str(t).strip()]
        if separator:
            return [t.strip() for t in text.split(separator) if t.strip()]
        return [text] if text else []
    return [str(state).strip()] if str(state).strip() else []


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
        self._trim = False
        self._strip_characters: str | Sequence[str] | None = None
        self._mark_as_required: bool | Callable[..., bool] | None = None
        self._disabled_on: set[str] = set()
        self._hidden_on: set[str] = set()
        self._visible_on: set[str] | None = None
        self._above_label: str | Callable[..., str] | None = None
        self._below_label: str | Callable[..., str] | None = None
        self._before_label: str | Callable[..., str] | None = None
        self._after_label: str | Callable[..., str] | None = None
        self._above_content: str | Callable[..., str] | None = None
        self._below_content: str | Callable[..., str] | None = None
        self._before_content: str | Callable[..., str] | None = None
        self._after_content: str | Callable[..., str] | None = None
        self._below_error: str | Callable[..., str] | None = None
        self._prefix_icon_color: str | None = None
        self._suffix_icon_color: str | None = None
        self._autocapitalize: str | None = None
        self._tel_regex: str | None = None
        self._length: int | None = None
        self._disable_option_when: Callable[..., bool] | None = None
        self._boolean_select = False
        self._preload = False
        self._wrap_labels = False
        # Toggle chrome (also used when Checkbox/Toggle share Field)
        self._on_color: str | None = None
        self._off_color: str | None = None
        self._on_icon: str | None = None
        self._off_icon: str | None = None
        self._inline: bool | None = None

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

    def shows_required_asterisk(self, **ctx: Any) -> bool:
        if self._mark_as_required is not None:
            return bool(evaluate(self._mark_as_required, **ctx))
        return self.is_required(**ctx)

    def is_disabled(self, **ctx: Any) -> bool:
        if super().is_disabled(**ctx):
            return True
        op = ctx.get("operation")
        if op is not None and self._disabled_on and str(op) in self._disabled_on:
            return True
        return False

    def is_visible(self, **ctx: Any) -> bool:
        if not super().is_visible(**ctx):
            return False
        op = ctx.get("operation")
        if op is not None:
            if self._hidden_on and str(op) in self._hidden_on:
                return False
            if self._visible_on is not None and str(op) not in self._visible_on:
                return False
        return True

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

    def trim(self, condition: bool = True) -> Self:
        """Strip leading/trailing whitespace on dehydrate (Filament ``trim``)."""
        self._trim = condition
        return self

    def strip_characters(self, characters: str | Sequence[str]) -> Self:
        """Remove listed characters from state on dehydrate (Filament ``stripCharacters``)."""
        self._strip_characters = characters
        return self

    def length(self, value: int) -> Self:
        """Exact character length validation (Filament ``length``)."""
        self._length = value
        return self.rules(f"size:{value}")

    def tel_regex(self, pattern: str) -> Self:
        """Custom telephone validation pattern (Filament ``telRegex``)."""
        self._tel_regex = pattern
        return self.rules(f"regex:{pattern}")

    def autocapitalize(self, value: str) -> Self:
        self._autocapitalize = value
        return self

    def mark_as_required(self, condition: bool | Callable[..., bool] = True) -> Self:
        """Show the required asterisk without adding a ``required`` rule."""
        self._mark_as_required = condition
        return self

    def disabled_on(self, *operations: str) -> Self:
        """Disable when Form/Schema ``operation`` is one of ``operations``."""
        self._disabled_on |= {str(op) for op in operations}
        return self

    def hidden_on(self, *operations: str) -> Self:
        self._hidden_on |= {str(op) for op in operations}
        return self

    def visible_on(self, *operations: str) -> Self:
        self._visible_on = {str(op) for op in operations}
        return self

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

    def below_error(self, content: str | Callable[..., str]) -> Self:
        self._below_error = content
        return self

    def prefix_icon_color(self, color: str) -> Self:
        self._prefix_icon_color = color
        return self

    def suffix_icon_color(self, color: str) -> Self:
        self._suffix_icon_color = color
        return self

    def disable_option_when(self, callback: Callable[..., bool]) -> Self:
        """Disable select/radio/checkbox-list options when callback returns True."""
        self._disable_option_when = callback
        return self

    def boolean(self, condition: bool = True) -> Self:
        """Use Yes/No options for Select/Radio (Filament ``boolean``)."""
        self._boolean_select = condition
        if condition:
            self._options = {1: "Yes", 0: "No"}
        return self

    def preload(self, condition: bool = True) -> Self:
        """Eager-load relationship options (fluent Filament ``preload``)."""
        self._preload = condition
        if isinstance(self._relationship, dict):
            self._relationship = {**self._relationship, "preload": condition}
        return self

    def wrap(self, condition: bool = True) -> Self:
        """Allow option labels to wrap (Filament select ``wrap``)."""
        self._wrap_labels = condition
        return self

    def on_color(self, color: str) -> Self:
        self._on_color = color
        return self

    def off_color(self, color: str) -> Self:
        self._off_color = color
        return self

    def on_icon(self, icon: str) -> Self:
        self._on_icon = icon
        return self

    def off_icon(self, icon: str) -> Self:
        self._off_icon = icon
        return self

    def inline(self, condition: bool = True) -> Self:
        """Inline checkbox/toggle/radio chrome (Filament ``inline``)."""
        self._inline = condition
        if condition:
            self._inline_label = True
        return self

    def active_url(self) -> Self:
        return self.rules("active_url")

    def ascii(self) -> Self:
        return self.rules("ascii")

    def alpha(self) -> Self:
        return self.rules("alpha")

    def alpha_dash(self) -> Self:
        return self.rules("alpha_dash")

    def alpha_num(self) -> Self:
        return self.rules("alpha_num")

    def confirmed(self) -> Self:
        return self.rules("confirmed")

    def different(self, field: str) -> Self:
        return self.rules(f"different:{field}")

    def same(self, field: str) -> Self:
        return self.rules(f"same:{field}")

    def filled(self) -> Self:
        return self.rules("filled")

    def present(self) -> Self:
        return self.rules("present")

    def ip(self) -> Self:
        return self.rules("ip")

    def ipv4(self) -> Self:
        return self.rules("ipv4")

    def ipv6(self) -> Self:
        return self.rules("ipv6")

    def mac_address(self) -> Self:
        return self.rules("mac_address")

    def json(self) -> Self:
        return self.rules("json")

    def ulid(self) -> Self:
        return self.rules("ulid")

    def uuid(self) -> Self:
        return self.rules("uuid")

    def hex_color(self) -> Self:
        return self.rules("hex_color")

    def multiple_of(self, value: int | float) -> Self:
        return self.rules(f"multiple_of:{value}")

    def doesnt_start_with(self, *values: str) -> Self:
        return self.rules("doesnt_start_with:" + ",".join(values))

    def doesnt_end_with(self, *values: str) -> Self:
        return self.rules("doesnt_end_with:" + ",".join(values))

    def starts_with(self, *values: str) -> Self:
        return self.rules("starts_with:" + ",".join(values))

    def ends_with(self, *values: str) -> Self:
        return self.rules("ends_with:" + ",".join(values))

    def required_with(self, *fields: str) -> Self:
        return self.rules("required_with:" + ",".join(fields))

    def required_with_all(self, *fields: str) -> Self:
        return self.rules("required_with_all:" + ",".join(fields))

    def required_without(self, *fields: str) -> Self:
        return self.rules("required_without:" + ",".join(fields))

    def required_without_all(self, *fields: str) -> Self:
        return self.rules("required_without_all:" + ",".join(fields))

    def required_if_accepted(self, field: str) -> Self:
        return self.rules(f"required_if_accepted:{field}")

    def prohibits(self, *fields: str) -> Self:
        return self.rules("prohibits:" + ",".join(fields))

    def after(self, date: str) -> Self:
        return self.rules(f"after:{date}")

    def after_or_equal(self, date: str) -> Self:
        return self.rules(f"after_or_equal:{date}")

    def before(self, date: str) -> Self:
        return self.rules(f"before:{date}")

    def before_or_equal(self, date: str) -> Self:
        return self.rules(f"before_or_equal:{date}")

    def date_equals(self, date: str) -> Self:
        return self.rules(f"date_equals:{date}")

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
        name: str | None = None,
        title_attribute: str | None = None,
        *,
        model: type[Any] | None = None,
        option_label: str | None = None,
        search_columns: Sequence[str] | None = None,
        preload: bool = False,
        modify_query: Callable[..., Any] | None = None,
        get_option_label: Callable[..., Any] | None = None,
        get_option_label_from_record_using: Callable[..., Any] | None = None,
    ) -> Self:
        """Wire options to an Eloquent-style relationship or related model.

        Filament parity:

        - ``relationship("author", "name")`` resolves the related model from the
          owning resource model in render context.
        - Pass ``model=Artist`` when the related class is known explicitly.
        - ``option_label="{name} - {bio}"`` formats labels from multiple columns.
        - ``get_option_label_from_record_using(lambda r: ...)`` for full control.
        - ``searchable()`` without ``preload()`` uses AJAX search (capped by
          ``options_limit``, default 50).
        - ``preload()`` eagerly loads a capped option set.
        """
        from almasix.orbit.forms.select_relationship import option_label_placeholders

        label_cb = get_option_label_from_record_using or get_option_label
        fmt = option_label
        placeholders = option_label_placeholders(fmt) if fmt else []
        title = title_attribute
        if title is None:
            title = placeholders[0] if placeholders else "id"
        cols = list(search_columns) if search_columns else None
        if cols is None and placeholders:
            cols = placeholders
        self._relationship = {
            "name": name,
            "title_attribute": title,
            "model": model,
            "option_label": fmt,
            "search_columns": cols,
            "preload": preload or self._preload,
            "modify_query": modify_query,
            "get_option_label": label_cb,
        }
        return self

    def get_option_label_from_record_using(self, callback: Callable[..., Any]) -> Self:
        """Filament alias — set label formatter on an existing relationship config."""
        if self._relationship is None:
            self._relationship = {
                "name": None,
                "title_attribute": "id",
                "model": None,
                "option_label": None,
                "search_columns": None,
                "preload": False,
                "modify_query": None,
                "get_option_label": callback,
            }
        else:
            self._relationship["get_option_label"] = callback
        return self

    def option_label(self, template: str) -> Self:
        """Set a ``{column}`` format string for relationship option labels.

        Example: ``.option_label("{name} - {country}")``.
        """
        from almasix.orbit.forms.select_relationship import option_label_placeholders

        placeholders = option_label_placeholders(template)
        if self._relationship is None:
            self._relationship = {
                "name": None,
                "title_attribute": placeholders[0] if placeholders else "id",
                "model": None,
                "option_label": template,
                "search_columns": placeholders or None,
                "preload": False,
                "modify_query": None,
                "get_option_label": None,
            }
        else:
            self._relationship["option_label"] = template
            if not self._relationship.get("search_columns") and placeholders:
                self._relationship["search_columns"] = placeholders
            if self._relationship.get("title_attribute") in (None, "id") and placeholders:
                self._relationship["title_attribute"] = placeholders[0]
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
        # Resource hosts store form state on ``data``; Conduit only accepts public
        # properties, so bind as ``data.{path}`` (see FormDataMutations.set_property).
        path = str(name or "")
        if path and not path.startswith("data."):
            path = f"data.{path}"
        return self.wire_model_attrs(path)

    def _common_input_attrs(self, **ctx: Any) -> str:
        parts: list[str] = []
        if self._autocomplete:
            parts.append(f'autocomplete="{e(self._autocomplete)}"')
        if self._autofocus:
            parts.append("autofocus")
        if self._input_mode:
            parts.append(f'inputmode="{e(self._input_mode)}"')
        if self._autocapitalize:
            parts.append(f'autocapitalize="{e(self._autocapitalize)}"')
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
        req = ' <span class="or-required">*</span>' if self.shows_required_asterisk(**ctx) else ""
        before = self._slot_html(self._before_label, "or-before-label", **ctx)
        after = self._slot_html(self._after_label, "or-after-label", **ctx)
        return (
            f"{before}<label class=\"or-label\" for=\"or-{name}\">"
            f"{e(self.get_label(**ctx))}{req}</label>{after}"
        )

    def _slot_html(self, content: str | Callable[..., str] | None, css: str, **ctx: Any) -> str:
        if content is None:
            return ""
        text = evaluate(content, **ctx)
        if text in (None, ""):
            return ""
        return f'<div class="{css}">{text}</div>'

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

            icon = ""
            if self._prefix_icon:
                color_c = f" or-color-{e(self._prefix_icon_color)}" if self._prefix_icon_color else ""
                icon = f'<span class="or-affix-icon{color_c}">{render_icon(self._prefix_icon)}</span>'
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

            icon = ""
            if self._suffix_icon:
                color_c = f" or-color-{e(self._suffix_icon_color)}" if self._suffix_icon_color else ""
                icon = f'<span class="or-affix-icon{color_c}">{render_icon(self._suffix_icon)}</span>'
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
        """Shared field chrome: label, hint, helper, content slots, wrapper attributes."""
        inline = " or-field-inline" if self._inline_label or self._inline else ""
        wrapper_attrs = self._attrs_to_html(
            {**self.get_extra_attributes(**ctx), **{
                k: evaluate(v, **ctx) for k, v in self._extra_field_wrapper_attributes.items()
            }}
        )
        body = (
            f"{self._slot_html(self._above_label, 'or-above-label', **ctx)}"
            f"{self._label_html(name, **ctx)}"
            f"{self._slot_html(self._below_label, 'or-below-label', **ctx)}"
            f"{self._hint_html(**ctx)}"
            f"{self._slot_html(self._above_content, 'or-above-content', **ctx)}"
            f"{self._slot_html(self._before_content, 'or-before-content', **ctx)}"
            f"{self._affix_wrap(control, **ctx)}"
            f"{self._slot_html(self._after_content, 'or-after-content', **ctx)}"
            f"{self._slot_html(self._below_content, 'or-below-content', **ctx)}"
            f"{self._helper_html(**ctx)}"
            f"{self._slot_html(self._below_error, 'or-below-error', **ctx)}"
        )
        return (
            f'<div class="or-field or-field-{type(self).__name__}{inline}" data-field="{name}"'
            f"{wrapper_attrs}>{body}</div>"
        )

    def apply_dehydrate_transforms(self, value: Any) -> Any:
        """Apply trim / strip_characters before custom dehydrate callbacks."""
        if value is None:
            return value
        text = str(value)
        if self._strip_characters:
            chars = (
                self._strip_characters
                if isinstance(self._strip_characters, str)
                else "".join(self._strip_characters)
            )
            text = text.translate({ord(c): None for c in chars})
        if self._trim:
            text = text.strip()
        return text if isinstance(value, str) or self._trim or self._strip_characters else value

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
                    "name", "title_attribute", "search_columns", "preload", "modify_query",
                    "get_option_label", "model", "option_label",
                } and not rel.get("search_columns") and not rel.get("preload")
                and rel.get("modify_query") is None and rel.get("get_option_label") is None
                and rel.get("model") is None and not rel.get("option_label")
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

    def effective_options_limit(self) -> int:
        from almasix.orbit.forms.select_relationship import DEFAULT_OPTIONS_LIMIT

        if self._options_limit is not None:
            return int(self._options_limit)
        return DEFAULT_OPTIONS_LIMIT

    def _owner_model(self, **ctx: Any) -> type[Any] | None:
        model = ctx.get("model")
        if isinstance(model, type):
            return model
        resource = ctx.get("resource")
        if resource is not None:
            getter = getattr(resource, "get_model", None)
            if callable(getter):
                try:
                    return getter()
                except Exception:
                    return getattr(resource, "model", None)
            return getattr(resource, "model", None)
        return None

    def resolve_relationship_options(
        self,
        state: Any = None,
        *,
        search: str | None = None,
        **ctx: Any,
    ) -> dict[str, str]:
        """Load relationship options for render or AJAX search."""
        from almasix.orbit.forms.select_relationship import (
            load_relationship_options,
            relationship_should_ajax,
            resolve_related_model,
        )

        rel = self.get_relationship()
        if not rel:
            return {}
        related = resolve_related_model(
            relationship_name=rel.get("name"),
            related_model=rel.get("model"),
            owner_model=self._owner_model(**ctx),
        )
        if related is None:
            return {}
        limit = self.effective_options_limit()
        title = str(rel.get("title_attribute") or "id")
        searchable = bool(self._searchable or not self._native)
        ajax = relationship_should_ajax(rel, searchable=searchable)

        selected = state if isinstance(state, (list, tuple, set)) else (
            [state] if state not in (None, "") else []
        )

        if ajax and not (search or "").strip():
            # Initial searchable render: only hydrate selected labels.
            if not selected:
                return {}
            return load_relationship_options(
                model=related,
                title_attribute=title,
                limit=limit,
                modify_query=rel.get("modify_query"),
                get_option_label=rel.get("get_option_label"),
                option_label=rel.get("option_label"),
                keys=list(selected),
            )

        return load_relationship_options(
            model=related,
            title_attribute=title,
            search=(search or "").strip() or None,
            search_columns=rel.get("search_columns"),
            limit=limit,
            modify_query=rel.get("modify_query"),
            get_option_label=rel.get("get_option_label"),
            option_label=rel.get("option_label"),
        )

    def uses_combobox(self) -> bool:
        """Filament: searchable / multiple / allowHtml / native(false) → custom combobox."""
        return bool(
            self._searchable
            or not self._native
            or self._multiple
            or self._allow_html
        )

    def _field_search_query(self, **ctx: Any) -> str:
        field_name = self.get_state_path() or self.get_name() or ""
        select_search = ctx.get("select_search") or {}
        if isinstance(select_search, dict) and field_name in select_search:
            return str(select_search.get(field_name) or "")
        return ""

    def _callback_options_for_render(self, state: Any, **ctx: Any) -> dict[str, str]:
        """Resolve ``get_search_results_using`` for the current AJAX search query."""
        cb = self._get_search_results_using
        if cb is None:
            return {}
        search = self._field_search_query(**ctx)
        raw = evaluate(cb, search, state=state, field=self, **ctx)
        if isinstance(raw, dict):
            return {str(k): str(v) for k, v in raw.items()}
        if isinstance(raw, (list, tuple)):
            out: dict[str, str] = {}
            for item in raw:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    out[str(item[0])] = str(item[1])
                elif isinstance(item, dict) and "value" in item:
                    out[str(item["value"])] = str(item.get("label", item["value"]))
            return out
        return {}

    def _relationship_options_for_render(self, state: Any, **ctx: Any) -> dict[str, str]:
        rel = self.get_relationship()
        if not rel:
            return {}
        # Explicit static options win over relationship resolution.
        if self._options not in (None, {}):
            return {}
        search = self._field_search_query(**ctx) or None
        return self.resolve_relationship_options(state, search=search, **ctx)

    def _options_overlay_for_render(self, state: Any, **ctx: Any) -> dict[str, str]:
        """Dynamic options from custom search callback or relationship loader."""
        if self._get_search_results_using is not None:
            return self._callback_options_for_render(state, **ctx)
        return self._relationship_options_for_render(state, **ctx)

    def _render_options_html(self, state: Any, **ctx: Any) -> str:
        # Merge relationship / custom-search options into the field for this render.
        overlay = self._options_overlay_for_render(state, **ctx)
        prior = self._options
        if overlay:
            # Keep selected labels available even when AJAX results omit them.
            selected = state if isinstance(state, (list, tuple, set)) else (
                [state] if state not in (None, "") else []
            )
            merged = dict(overlay)
            if isinstance(prior, dict):
                for key in selected:
                    sk = str(key)
                    if sk and sk not in merged and sk in {str(k) for k in prior}:
                        merged[sk] = str(prior[key] if key in prior else prior.get(sk, sk))
            self._options = merged
        try:
            selected = state if isinstance(state, (list, tuple, set)) else (
                [state] if state not in (None, "") else []
            )
            selected_s = {str(s) for s in selected}
            chunks: list[str] = []
            count = 0
            limit = self._options_limit
            if self.get_relationship() is not None and limit is None:
                from almasix.orbit.forms.select_relationship import DEFAULT_OPTIONS_LIMIT

                limit = DEFAULT_OPTIONS_LIMIT
            for group_label, opts in self.get_option_groups(**ctx):
                inner = []
                for k, v in opts.items():
                    if limit is not None and count >= limit:
                        break
                    if self._disable_option_when is not None and evaluate(
                        self._disable_option_when, value=k, label=v, state=state, **ctx
                    ):
                        disabled_opt = " disabled"
                    else:
                        disabled_opt = ""
                    sel = " selected" if str(k) in selected_s else ""
                    label = str(v) if self._allow_html else e(v)
                    wrap_cls = ' class="or-option-wrap"' if self._wrap_labels else ""
                    group_attr = f' data-group="{e(group_label)}"' if group_label else ""
                    inner.append(
                        f'<option value="{e(k)}" data-label="{e(v)}"{group_attr}'
                        f"{sel}{disabled_opt}{wrap_cls}>{label}</option>"
                    )
                    count += 1
                body = "".join(inner)
                if group_label:
                    chunks.append(f'<optgroup label="{e(group_label)}">{body}</optgroup>')
                else:
                    chunks.append(body)
            return "".join(chunks)
        finally:
            self._options = prior

    def _select_meta_attrs(self, *, searchable: bool) -> str:
        rel = self.get_relationship()
        attrs = ""
        if rel:
            if rel.get("name"):
                attrs += f' data-relationship="{e(rel["name"])}"'
            if rel.get("search_columns"):
                attrs += f' data-search-columns="{e(",".join(rel["search_columns"]))}"'
            if rel.get("preload"):
                attrs += ' data-preload="true"'
            from almasix.orbit.forms.select_relationship import relationship_should_ajax

            if relationship_should_ajax(rel, searchable=searchable):
                attrs += ' data-ajax-search="true"'
            attrs += f' data-options-limit="{self.effective_options_limit()}"'
        if self._get_search_results_using is not None:
            attrs += ' data-ajax-search="true"'
        if self._no_search_results_message:
            attrs += f' data-no-results="{e(self._no_search_results_message)}"'
        if self._loading_message:
            attrs += f' data-loading="{e(self._loading_message)}"'
        if self._searching_message:
            attrs += f' data-searching="{e(self._searching_message)}"'
        if self._min_items is not None:
            attrs += f' data-min-items="{self._min_items}"'
        if self._max_items is not None:
            attrs += f' data-max-items="{self._max_items}"'
        if self._reorderable_selected:
            attrs += ' data-reorderable="true"'
        if not self._native:
            attrs += ' data-native="false"'
        if self._allow_html:
            attrs += ' data-allow-html="true"'
        if self._multiple:
            attrs += ' data-multiple="true"'
        return attrs

    def _select_actions_html(self, name: str) -> str:
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
        return f'<div class="or-select-actions">{"".join(actions)}</div>' if actions else ""

    def _render_combobox(
        self,
        *,
        name: str,
        opts_html: str,
        state: Any,
        searchable: bool,
        **ctx: Any,
    ) -> str:
        multi = " multiple" if self._multiple else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        wire = self._wire_binding(name)
        debounce = self._search_debounce or 200
        prompt = e(self._search_prompt or "Search…")
        placeholder = "—" if self._selectable_placeholder else ""
        query = e(self._field_search_query(**ctx))
        no_results = e(self._no_search_results_message or "No options match your search.")
        searching = e(self._searching_message or "Searching…")
        loading = e(self._loading_message or "Loading…")
        placeholder_opt = ""
        if self._selectable_placeholder and not self._multiple:
            placeholder_opt = f'<option value="">{e(placeholder)}</option>'
        meta = self._select_meta_attrs(searchable=searchable)
        searchable_attr = " data-searchable" if searchable else ""
        return (
            f'<div class="or-combobox" x-data="orbitCombobox"'
            f'{searchable_attr}{meta}'
            f' data-placeholder="{e(placeholder)}"'
            f' data-search-prompt="{prompt}"'
            f' data-no-results="{no_results}"'
            f' data-searching="{searching}"'
            f' data-loading="{loading}"'
            f' data-debounce="{debounce}"'
            f'{" data-wrap-labels" if self._wrap_labels else ""}'
            f' @keydown.escape.window="close()"'
            f' @click.outside="close()">'
            f'<select class="or-select or-combobox-native" id="or-{name}" name="{name}"'
            f'{multi}{disabled} x-ref="select"{wire}{self._after_state_attr()} '
            f'tabindex="-1" aria-hidden="true">{placeholder_opt}{opts_html}</select>'
            f'<div class="or-combobox-control" :class="{{ \'is-open\': open, \'is-disabled\': disabled }}">'
            f'<div class="or-combobox-trigger" x-ref="trigger" role="combobox" '
            f'tabindex="0" @click="toggle()" @keydown.down.prevent="move(1)" '
            f'@keydown.up.prevent="move(-1)" @keydown.enter.prevent="chooseActive()" '
            f'@keydown.space.prevent="toggle()" '
            f':aria-expanded="open.toString()" aria-haspopup="listbox" '
            f':aria-disabled="disabled.toString()" id="or-{name}-trigger">'
            f'<div class="or-combobox-value">'
            f'<template x-for="item in selectedItems" :key="item.value">'
            f'<span class="or-combobox-chip" x-show="multiple">'
            f'<span class="or-combobox-chip-label" x-text="item.label"></span>'
            f'<button type="button" class="or-combobox-chip-remove" '
            f'@click.stop="deselect(item.value)" :aria-label="`Remove ${{item.label}}`">'
            f'<span aria-hidden="true">×</span></button></span>'
            f"</template>"
            f'<span class="or-combobox-single" '
            f'x-show="!multiple && selectedLabel && !(searchable && open)" '
            f'x-text="selectedLabel"></span>'
            f'<span class="or-combobox-placeholder" '
            f'x-show="!multiple && !selectedLabel && !(searchable && open)" '
            f'x-text="placeholder"></span>'
            f'<input type="search" class="or-combobox-search" x-ref="search" '
            f'x-show="searchable" x-model="q" value="{query}" '
            f'placeholder="{prompt}" autocomplete="off" '
            f'@focus="openPanel()" '
            f'@click.stop="openPanel()" '
            f'@input.debounce.{debounce}ms="onSearch()" '
            f'@keydown.down.prevent="move(1)" '
            f'@keydown.up.prevent="move(-1)" '
            f'@keydown.enter.prevent="chooseActive()" '
            f'@keydown.backspace="onBackspace($event)" '
            f'aria-autocomplete="list" aria-controls="or-{name}-list" '
            f':aria-expanded="open.toString()" />'
            f"</div>"
            f'<button type="button" class="or-combobox-clear" x-show="hasValue && !disabled" '
            f'@click.stop="clear()" aria-label="Clear selection">'
            f'<span aria-hidden="true">×</span></button>'
            f'<span class="or-combobox-chevron" aria-hidden="true"></span>'
            f"</div>"
            f'<ul class="or-combobox-dropdown" x-ref="list" id="or-{name}-list" '
            f'role="listbox" x-show="open" '
            f':aria-activedescendant="activeId">'
            f'<li class="or-combobox-status" x-show="statusMessage" x-text="statusMessage"></li>'
            f'<template x-for="(opt, idx) in visibleOptions" :key="opt.value">'
            f'<li class="or-combobox-option" role="option" '
            f':id="`or-{name}-opt-${{idx}}`" '
            f':class="{{ '
            f"'is-active': idx === activeIndex, "
            f"'is-selected': isSelected(opt.value), "
            f"'is-disabled': opt.disabled, "
            f"'or-option-wrap': wrapLabels "
            f'}}" '
            f':aria-selected="isSelected(opt.value).toString()" '
            f'@mouseenter="activeIndex = idx" '
            f'@click="choose(opt)" '
            f'x-html="allowHtml ? opt.labelHtml : undefined" '
            f'x-text="allowHtml ? \'\' : opt.label"></li>'
            f"</template></ul></div>"
            f"{self._select_actions_html(name)}"
            f"</div>"
        )

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        opts_html = self._render_options_html(state, **ctx)
        searchable = self._searchable or not self._native
        # Filament: multiple / allowHtml force the custom select even when native().
        if self.uses_combobox():
            control = self._render_combobox(
                name=name,
                opts_html=opts_html,
                state=state,
                searchable=searchable or self._multiple or self._allow_html,
                **ctx,
            )
            html = self.wrap_field(name, control, **ctx)
            return html.replace(
                f'data-field="{name}"',
                f'data-field="{name}" data-combobox',
                1,
            )

        multi = " multiple" if self._multiple else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        wire = self._wire_binding(name)
        meta = self._select_meta_attrs(searchable=False)
        placeholder_opt = ""
        if self._selectable_placeholder and not self._multiple:
            placeholder_opt = '<option value="">—</option>'
        control = (
            f'<select class="or-select" id="or-{name}" name="{name}"{multi}{disabled}'
            f"{wire}{self._after_state_attr()}>{placeholder_opt}{opts_html}</select>"
            f"{self._select_actions_html(name)}"
        )
        html = self.wrap_field(name, control, **ctx)
        return html.replace(f'data-field="{name}"', f'data-field="{name}"{meta}', 1)


class Checkbox(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        checked = " checked" if state else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        inline = " or-field-inline" if self._inline or self._inline_label else ""
        return (
            f'<div class="or-field or-field-Checkbox{inline}" data-field="{name}">'
            f'<label class="or-checkbox-label"><input class="or-checkbox" type="checkbox" '
            f'name="{name}"{self._wire_binding(name)}{checked}{disabled} /> {label}</label></div>'
        )


class Toggle(Checkbox):
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        html = html.replace("or-field-Checkbox", "or-field-Toggle").replace("or-checkbox", "or-toggle")
        color_attrs = ""
        if self._on_color:
            color_attrs += f' data-on-color="{e(self._on_color)}"'
        if self._off_color:
            color_attrs += f' data-off-color="{e(self._off_color)}"'
        if color_attrs:
            html = html.replace('class="or-toggle"', f'class="or-toggle"{color_attrs}', 1)
        if self._on_icon or self._off_icon:
            from almasix.orbit.support.icons import icon as render_icon

            icons = ""
            if self._on_icon:
                icons += f'<span class="or-toggle-on-icon">{render_icon(self._on_icon)}</span>'
            if self._off_icon:
                icons += f'<span class="or-toggle-off-icon">{render_icon(self._off_icon)}</span>'
            html = html.replace("</label>", f"{icons}</label>", 1)
        return html

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
    """Calendar-day picker (Flowbite by default; ``.native(True)`` for browser input)."""

    _mode: str = "date"
    _native_input_type: str = "date"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = self._native_input_type
        self._min_date: str | None = None
        self._max_date: str | None = None
        self._display_format: str | None = None
        # Flowbite calendar is the default (Shamar parity); opt into native HTML.
        self._native = False
        self._seconds = False
        self._time_format: str | None = None
        self._minute_step: int | None = None

    def min_date(self, value: str) -> Self:
        self._min_date = value
        return self

    def max_date(self, value: str) -> Self:
        self._max_date = value
        return self

    def display_format(self, fmt: str) -> Self:
        """Soft display hint for the Flowbite host (locale Intl remains the default)."""
        self._display_format = fmt
        return self

    def native(self, condition: bool = True) -> Self:
        self._native = condition
        return self

    def seconds(self, condition: bool = True) -> Self:
        self._seconds = bool(condition)
        if self._seconds:
            self._step = 1
        return self

    def time_format(self, value: str) -> Self:
        """Display clock as ``12`` or ``24``; stored values stay 24-hour."""
        token = str(value).strip()
        if token in {"12", "24"}:
            self._time_format = token
        return self

    def hours12(self) -> Self:
        return self.time_format("12")

    def hours24(self) -> Self:
        return self.time_format("24")

    def minute_step(self, value: int) -> Self:
        try:
            step = int(value)
        except (TypeError, ValueError):
            step = 5
        self._minute_step = max(1, min(30, step))
        return self

    def _native_type_for_mode(self) -> str:
        return {
            "date": "date",
            "datetime": "datetime-local",
            "time": "time",
            "week": "week",
            "month": "month",
            "year": "number",
        }.get(self._mode, "date")

    def _render_native(self, state: Any = None, **ctx: Any) -> str:
        name = e(self.get_state_path() or "")
        placeholder = self.get_placeholder(**ctx)
        ph = f' placeholder="{e(placeholder)}"' if placeholder else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        readonly = " readonly" if self._readonly else ""
        val = "" if state is None else e(str(state))
        attrs: list[str] = []
        input_type = self._native_type_for_mode()
        if self._min_date:
            attrs.append(f'min="{e(self._min_date)}"')
        if self._max_date:
            attrs.append(f'max="{e(self._max_date)}"')
        if self._display_format:
            attrs.append(f'data-display-format="{e(self._display_format)}"')
        if self._seconds and self._mode in {"datetime", "time"} and self._step is None:
            attrs.append('step="1"')
        if self._mode == "year":
            attrs.append('inputmode="numeric"')
            attrs.append('min="1900"')
            attrs.append('max="2100"')
        attr_s = (" " + " ".join(attrs)) if attrs else ""
        control = (
            f'<input class="or-input" id="or-{name}" name="{name}" type="{e(input_type)}" '
            f'value="{val}"{ph}{disabled}{readonly}{attr_s}{self._common_input_attrs(**ctx)}'
            f'{self._wire_binding(name)}{self._after_state_attr()} />'
        )
        return self.wrap_field(name, control, **ctx)

    def _calendar_icon(self) -> str:
        return (
            '<div class="or-datepicker__icon" aria-hidden="true">'
            '<svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">'
            '<path fill-rule="evenodd" d="M5.75 2a.75.75 0 01.75.75V4h7V2.75a.75.75 0 '
            "011.5 0V4h.25A2.75 2.75 0 0118 6.75v8.5A2.75 2.75 0 0115.25 18H4.75A2.75 "
            "2.75 0 012 15.25v-8.5A2.75 2.75 0 014.75 4H5V2.75A.75.75 0 015.75 2zm-1 "
            "5.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h10.5c.69 0 "
            '1.25-.56 1.25-1.25v-6.5c0-.69-.56-1.25-1.25-1.25H4.75z" clip-rule="evenodd" />'
            "</svg></div>"
        )

    def _clock_icon(self) -> str:
        return (
            '<div class="or-datepicker__icon" aria-hidden="true">'
            '<svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">'
            '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-13a.75.75 '
            "0 00-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 000-1.5h-3.25V5z\" "
            'clip-rule="evenodd" /></svg></div>'
        )

    def _render_time_controls(self, *, field_id: bool, label: str) -> str:
        id_attr = f' id="or-{e(label)}"' if field_id else ""
        return (
            f'<div class="relative or-datepicker__time-wrap" x-ref="timeWrap">'
            f"{self._clock_icon()}"
            f'<div class="or-timepicker__control">'
            f'<input{id_attr} type="text" autocomplete="off" spellcheck="false" '
            f'class="or-input or-datepicker__time or-timepicker__input" '
            f':inputmode="timeFormat === \'12\' ? \'text\' : \'numeric\'" '
            f':placeholder="timePlaceholder" :disabled="disabled" '
            f':aria-label="{e(label)} time" :value="timeDraft" '
            f'@focus="onTimeFocus()" @keydown="onTimeKeydown($event)" '
            f'@paste="onTimePaste($event)" @blur="commitTimeDraft()" '
            f'@click="openTimeAssist()" />'
            f'<button type="button" class="or-timepicker__toggle" @click="toggleTime()" '
            f':disabled="disabled" :aria-expanded="timeOpen ? \'true\' : \'false\'" '
            f'aria-label="Adjust time" tabindex="-1">'
            f'<svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" '
            f'aria-hidden="true"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 '
            "011.06.02L10 11.17l3.71-3.94a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 "
            '01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" /></svg>'
            f"</button></div>"
            f'<div class="or-timepicker" x-show="timeOpen" x-cloak '
            f'x-transition.opacity.duration.120ms role="dialog" aria-label="Adjust time">'
            f'<div class="or-timepicker__steppers" '
            f':class="{{ \'has-seconds\': seconds, \'has-meridiem\': timeFormat === \'12\' }}">'
            f'<div class="or-timepicker__stepper">'
            f'<button type="button" class="or-timepicker__spin" @click="nudge(\'hour\', 1)" '
            f'aria-label="Increase hour">+</button>'
            f'<div class="or-timepicker__digit" x-text="displayHour"></div>'
            f'<button type="button" class="or-timepicker__spin" @click="nudge(\'hour\', -1)" '
            f'aria-label="Decrease hour">−</button>'
            f'<span class="or-timepicker__unit">Hr</span></div>'
            f'<div class="or-timepicker__sep" aria-hidden="true">:</div>'
            f'<div class="or-timepicker__stepper">'
            f'<button type="button" class="or-timepicker__spin" @click="nudge(\'minute\', 1)" '
            f'aria-label="Increase minute">+</button>'
            f'<div class="or-timepicker__digit" x-text="padTime(minute)"></div>'
            f'<button type="button" class="or-timepicker__spin" @click="nudge(\'minute\', -1)" '
            f'aria-label="Decrease minute">−</button>'
            f'<span class="or-timepicker__unit">Min</span></div>'
            f'<template x-if="seconds"><div class="or-timepicker__seconds">'
            f'<div class="or-timepicker__sep" aria-hidden="true">:</div>'
            f'<div class="or-timepicker__stepper">'
            f'<button type="button" class="or-timepicker__spin" @click="nudge(\'second\', 1)" '
            f'aria-label="Increase second">+</button>'
            f'<div class="or-timepicker__digit" x-text="padTime(second)"></div>'
            f'<button type="button" class="or-timepicker__spin" @click="nudge(\'second\', -1)" '
            f'aria-label="Decrease second">−</button>'
            f'<span class="or-timepicker__unit">Sec</span></div></div></template>'
            f'<template x-if="timeFormat === \'12\'">'
            f'<div class="or-timepicker__stepper or-timepicker__meridiem">'
            f'<button type="button" class="or-timepicker__spin" @click="nudge(\'meridiem\', 1)" '
            f'aria-label="Toggle AM/PM">+</button>'
            f'<div class="or-timepicker__digit" x-text="meridiem"></div>'
            f'<button type="button" class="or-timepicker__spin" @click="nudge(\'meridiem\', 1)" '
            f'aria-label="Toggle AM/PM">−</button>'
            f'<span class="or-timepicker__unit"> </span></div></template>'
            f"</div>"
            f'<div class="or-timepicker__chips">'
            f'<button type="button" class="or-timepicker__chip" @click="setTimeNow()">Now</button>'
            f'<button type="button" class="or-timepicker__chip" @click="clearTime()">Clear</button>'
            f"</div></div></div>"
        )

    def _render_flowbite(self, state: Any = None, **ctx: Any) -> str:
        name = e(self.get_state_path() or "")
        path = f"data.{name}" if name and not str(name).startswith("data.") else name
        val = "" if state is None else e(str(state))
        disabled = self.is_disabled(**ctx) or self._readonly
        disabled_cls = " is-disabled" if disabled else ""
        disabled_attr = " disabled" if disabled else ""
        placeholder = e(self.get_placeholder(**ctx) or "")
        seconds = "true" if self._seconds else "false"
        time_format = e(self._time_format or "")
        minute_step = (
            str(self._minute_step) if self._minute_step is not None else ""
        )
        min_date = e(self._min_date or "")
        max_date = e(self._max_date or "")
        label = e(self.get_label(**ctx))
        mode = e(self._mode)

        date_block = ""
        if self._mode != "time":
            date_block = (
                f'<div class="or-datepicker__host" x-ref="pickerHost">'
                f"{self._calendar_icon()}"
                f'<input id="or-{name}" x-ref="dateInput" type="text" autocomplete="off" '
                f'class="or-input or-datepicker__input" '
                f':placeholder="placeholder || defaultPlaceholder" :disabled="disabled" '
                f':aria-label="{label}" />'
                f"</div>"
            )

        time_block = ""
        if self._mode in {"datetime", "time"}:
            time_block = self._render_time_controls(
                field_id=self._mode == "time",
                label=name,
            )

        host = (
            f'<div class="or-datepicker or-datepicker--{mode}{disabled_cls}" '
            f'data-mode="{mode}" data-seconds="{seconds}" '
            f'data-time-format="{time_format}" data-minute-step="{e(minute_step)}" '
            f'data-min="{min_date}" data-max="{max_date}" '
            f'data-placeholder="{placeholder}" data-path="{e(path)}" '
            f'x-data="orbitDatePicker" @keydown.escape.window="onEscape()" '
            f'wire:ignore conduit:ignore>'
            f'<input type="hidden" x-ref="state" id="or-{name}-state" name="{name}" '
            f'value="{val}"{disabled_attr}{self._wire_binding(name)}'
            f'{self._after_state_attr()} />'
            f'<div class="or-datepicker__row">{date_block}{time_block}</div>'
            f"</div>"
        )
        return self.wrap_field(name, host, **ctx)

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        if self._native:
            return self._render_native(state, **ctx)
        return self._render_flowbite(state, **ctx)


class DateTimePicker(DatePicker):
    _mode = "datetime"
    _native_input_type = "datetime-local"


class TimePicker(DatePicker):
    _mode = "time"
    _native_input_type = "time"


class WeekPicker(DatePicker):
    """ISO week picker — stores the Monday of the selected week (``YYYY-MM-DD``)."""

    _mode = "week"
    _native_input_type = "week"


class MonthPicker(DatePicker):
    """Month picker — stores the first day of the month (``YYYY-MM-DD``)."""

    _mode = "month"
    _native_input_type = "month"


class YearPicker(DatePicker):
    """Year picker — stores a four-digit year (``YYYY``)."""

    _mode = "year"
    _native_input_type = "number"


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
        self._upload_url: str | None = None

    def upload_url(self, url: str) -> Self:
        """Endpoint the browser posts selected files to.

        Panels set this automatically; override when a form lives outside a panel.
        """
        self._upload_url = url
        return self

    def get_upload_rules(self) -> Any:
        """Server-side rules the upload endpoint enforces for this field."""
        from almasix.orbit.forms.uploads import UploadRules

        return UploadRules(
            disk=self._disk,
            directory=self._directory,
            visibility=self._visibility,
            preserve_filenames=self._preserve_filenames,
            max_size=self._max_size,
            min_size=self._min_size,
            accepted_types=list(self._accepted_file_types),
        )

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

    def _existing_files_payload(self, state: Any) -> list[dict[str, str]]:
        """JSON-serializable existing files for FilePond ``files``."""
        from almasix.orbit.forms.uploads import is_image

        values = state if isinstance(state, (list, tuple)) else ([state] if state else [])
        out: list[dict[str, str]] = []
        for value in values:
            if isinstance(value, dict):
                path = str(value.get("path") or value.get("url") or "")
                url = str(value.get("url") or path)
                label = str(value.get("name") or path.rsplit("/", 1)[-1])
                mime = str(value.get("mime") or ("image/*" if is_image(path) else ""))
            else:
                path = str(value or "")
                url = path
                label = path.rsplit("/", 1)[-1] if path else ""
                mime = "image/*" if is_image(path) else ""
            if not path:
                continue
            out.append({"path": path, "url": url, "name": label, "mime": mime})
        return out

    def _render_existing_files(self, state: Any) -> str:
        """Legacy card chrome (kept for progressive enhancement / tests)."""
        from almasix.orbit.forms.uploads import is_image

        values = state if isinstance(state, (list, tuple)) else ([state] if state else [])
        cards: list[str] = []
        for value in values:
            if isinstance(value, dict):
                path = str(value.get("path") or value.get("url") or "")
                url = str(value.get("url") or path)
                label = str(value.get("name") or path.rsplit("/", 1)[-1])
            else:
                path = str(value or "")
                url = path
                label = path.rsplit("/", 1)[-1]
            if not path:
                continue
            body = (
                f'<img class="or-file-thumb" src="{e(url)}" alt="{e(label)}" />'
                if is_image(path)
                else f'<span class="or-file-name">{e(label)}</span>'
            )
            actions = ""
            if self._openable:
                actions += (
                    f'<a class="or-file-action" href="{e(url)}" target="_blank" '
                    'rel="noopener">Open</a>'
                )
            if self._downloadable:
                actions += f'<a class="or-file-action" href="{e(url)}" download>Download</a>'
            cards.append(
                f'<div class="or-file-card" data-file-path="{e(path)}">{body}'
                f'<div class="or-file-card-actions">{actions}'
                '<button type="button" class="or-file-remove" data-file-remove '
                'aria-label="Remove file">&times;</button></div></div>'
            )
        return "".join(cards)

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        import json

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
        existing = self._existing_files_payload(state)
        if existing:
            attrs.append(f'data-existing="{e(json.dumps(existing))}"')
        upload_url = self._upload_url or ctx.get("upload_url")
        if upload_url:
            attrs.append(f'data-upload-url="{e(str(upload_url))}"')
        field_key = self.get_state_path() or self.get_name() or ""
        attrs.append(f'data-upload-field="{e(field_key)}"')
        # Conduit public path — FormDataMutations accepts ``data.*``.
        upload_path = field_key if str(field_key).startswith("data.") else f"data.{field_key}"
        attrs.append(f'data-upload-path="{e(upload_path)}"')
        resource = ctx.get("resource")
        slug_fn = getattr(resource, "get_slug", None)
        if callable(slug_fn):
            attrs.append(f'data-upload-resource="{e(str(slug_fn()))}"')
        attr_str = (" " + " ".join(attrs)) if attrs else ""
        avatar_cls = " or-file-avatar" if self._avatar else ""
        panel_cls = " or-file-panel" if self._panel_layout else ""
        # Noscript / progressive-enhancement preview for existing files.
        preview = ""
        if self._previewable and existing:
            preview = (
                '<div class="or-file-preview or-file-preview-fallback" data-preview-grid '
                f'aria-live="polite">{self._render_existing_files(state)}</div>'
            )
        control = (
            f"{preview}"
            # No wire:model — FilePond owns the input; state syncs via data-upload-path + $set.
            f'<input class="or-file" id="or-{name}" type="file" name="{name}"{acc}{multi}{disabled} />'
        )
        html = self.wrap_field(name, control, **ctx)
        # Conduit morph must not replace FilePond chrome (parity with Livewire wire:ignore).
        return html.replace(
            'class="or-field or-field-FileUpload"',
            f'class="or-field or-field-FileUpload{avatar_cls}{panel_cls}" '
            f'wire:ignore conduit:ignore',
            1,
        ).replace(f'data-field="{name}"', f'data-field="{name}"{attr_str}', 1)


class Radio(Select):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        wire = self._wire_binding(name)
        opts = []
        for k, v in self.get_options(**ctx).items():
            checked = " checked" if str(k) == str(state) else ""
            desc = self._option_descriptions.get(str(k))
            desc_html = f'<span class="or-option-desc">{e(desc)}</span>' if desc else ""
            opts.append(
                f'<label class="or-radio-label"><input type="radio" class="or-radio" '
                f'name="{name}" value="{e(k)}"{wire}{checked}{disabled} /> '
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
        selected_list = [str(s) for s in _normalize_string_list(state)]
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        options = self.get_options(**ctx)
        option_keys = [str(k) for k in options.keys()]
        opts = []
        for k, v in options.items():
            key = str(k)
            desc = self._option_descriptions.get(key)
            desc_html = f'<span class="or-option-desc">{e(desc)}</span>' if desc else ""
            # Alpine x-model on an array — no :checked (that fights native + Conduit morph).
            opts.append(
                f'<label class="or-checkbox-label">'
                f'<input type="checkbox" class="or-checkbox" name="{name}" value="{e(key)}" '
                f'x-model="selected"{disabled} /> '
                f'<span class="or-option-body"><span class="or-option-label">{e(v)}</span>{desc_html}</span></label>'
            )
        bulk = ""
        if self._bulk_toggle:
            bulk = (
                '<div class="or-checkbox-list-bulk">'
                '<button type="button" class="or-link-btn or-link-primary" '
                'data-select-all @click.prevent="selectAll()">Select all</button>'
                '<span class="or-checkbox-list-bulk-sep" aria-hidden="true">·</span>'
                '<button type="button" class="or-link-btn or-link-danger" '
                'data-deselect-all @click.prevent="deselectAll()">Deselect all</button>'
                "</div>"
            )
        cols = f' style="--or-options-cols:{self._options_columns}"' if self._options_columns else ""
        cols_cls = f" or-options-cols-{self._options_columns}" if self._options_columns else ""
        state_json = e(json.dumps(selected_list))
        options_json = e(json.dumps(option_keys))
        path = f"data.{name}" if name and not str(name).startswith("data.") else name
        # wire:ignore + key — keep Alpine tree across Conduit morphs; sync via sync_data_path.
        return (
            f'<div class="or-field or-field-CheckboxList{cols_cls}" data-field="{name}" '
            f'data-path="{e(path)}" data-state="{state_json}" data-options="{options_json}" '
            f'wire:key="checkbox-list-{name}" conduit:key="checkbox-list-{name}" '
            f'x-data="orbitCheckboxList" wire:ignore conduit:ignore{cols}>'
            f'<span class="or-label">{label}</span>{bulk}'
            f'<div class="or-checkbox-list">{"".join(opts)}</div></div>'
        )


class TagsInput(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._suggestions: list[str] = []
        self._separator: str = ","
        self._reorderable = False
        self._split_keys: list[str] | None = None
        self._tag_prefix: str = ""
        self._tag_suffix: str = ""

    def suggestions(self, items: Sequence[str]) -> Self:
        self._suggestions = list(items)
        return self

    def separator(self, value: str) -> Self:
        self._separator = value
        return self

    def split_keys(self, keys: Sequence[str]) -> Self:
        """Keys that commit the current draft tag (in addition to Enter)."""
        self._split_keys = [str(k) for k in keys]
        return self

    def reorderable(self, condition: bool = True) -> Self:
        self._reorderable = condition
        return self

    def tag_prefix(self, value: str) -> Self:
        self._tag_prefix = value
        return self

    def tag_suffix(self, value: str) -> Self:
        self._tag_suffix = value
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        tags = _normalize_string_list(state, separator=self._separator)
        disabled = bool(self.is_disabled(**ctx) or self._readonly)
        disabled_attr = " disabled" if disabled else ""
        suggestions = ""
        list_attr = ""
        if self._suggestions:
            opts = "".join(f'<option value="{e(s)}"></option>' for s in self._suggestions)
            suggestions = f'<datalist id="or-{name}-suggestions">{opts}</datalist>'
            list_attr = f' list="or-{name}-suggestions"'
        reorder = ' data-reorderable="true"' if self._reorderable else ""
        split_keys = list(self._split_keys) if self._split_keys is not None else []
        if self._separator and self._separator not in split_keys:
            split_keys = [*split_keys, self._separator]
        if "Tab" not in split_keys:
            split_keys = [*split_keys, "Tab"]
        path = f"data.{name}" if name and not str(name).startswith("data.") else name
        state_json = e(json.dumps(tags))
        split_json = e(json.dumps(split_keys))
        prefix = e(self._tag_prefix)
        suffix = e(self._tag_suffix)
        placeholder = e(self.get_placeholder(**ctx) or "New tag")
        # Alpine-driven chips + draft input; state synced via FormDataMutations.sync_data_path.
        return (
            f'<div class="or-field or-field-TagsInput" data-field="{name}" '
            f'data-path="{e(path)}" data-state="{state_json}" data-split-keys="{split_json}" '
            f'data-separator="{e(self._separator)}" data-tag-prefix="{prefix}" '
            f'data-tag-suffix="{suffix}"{reorder} '
            f'wire:key="tags-input-{name}" conduit:key="tags-input-{name}" '
            f'x-data="orbitTagsInput" wire:ignore conduit:ignore">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<div class="or-tags-input-wrap" @click="$refs.tagInput && $refs.tagInput.focus()">'
            f'<template x-for="tag in state" :key="tag">'
            f'<span class="or-tag">'
            f'<span class="or-tag-prefix" x-text="tagPrefix" x-show="tagPrefix"></span>'
            f'<span class="or-tag-label" x-text="tag"></span>'
            f'<span class="or-tag-suffix" x-text="tagSuffix" x-show="tagSuffix"></span>'
            f'<button type="button" class="or-tag-remove" @click.stop="deleteTag(tag)" '
            f'aria-label="Remove tag" x-show="!disabled">×</button>'
            f"</span></template>"
            f'<input class="or-tags-input" id="or-{name}" name="{name}" type="text" '
            f'x-ref="tagInput" x-model="newTag" placeholder="{placeholder}" autocomplete="off" '
            f'@keydown.enter.prevent="createTag()" @keydown.tab.prevent="createTag()" '
            f'@keydown="onKeydown($event)" @blur="createTag()" @paste="onPaste($event)" '
            f'{disabled_attr}{list_attr} />'
            f"</div>{suggestions}</div>"
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


#: Toolbar buttons the editor knows how to execute, with their labels.
RICH_EDITOR_TOOLS: dict[str, str] = {
    "bold": "Bold",
    "italic": "Italic",
    "underline": "Underline",
    "strike": "Strikethrough",
    "link": "Link",
    "unlink": "Unlink",
    "h1": "Heading 1",
    "h2": "Heading 2",
    "h3": "Heading 3",
    "heading": "Heading",
    "paragraph": "Paragraph",
    "blockquote": "Quote",
    "codeBlock": "Code block",
    "bulletList": "Bullet list",
    "orderedList": "Numbered list",
    "horizontalRule": "Divider",
    "image": "Image",
    "alignStart": "Align left",
    "alignCenter": "Align center",
    "alignEnd": "Align right",
    "clearFormat": "Clear formatting",
    "undo": "Undo",
    "redo": "Redo",
}


class RichEditor(Textarea):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._toolbar_buttons: list[str] = ["bold", "italic", "link"]
        self._placeholder: str | None = None
        self._merge_tags: list[str] = []
        self._custom_tools: dict[str, str] = {}
        self._min_height: str | None = None

    def toolbar_buttons(self, buttons: Sequence[str]) -> Self:
        self._toolbar_buttons = list(buttons)
        return self

    def get_toolbar_buttons(self) -> list[str]:
        return list(self._toolbar_buttons)

    def toolbar_button(self, name: str, label: str | None = None) -> Self:
        """Append one button, optionally with your own label."""
        if name not in self._toolbar_buttons:
            self._toolbar_buttons.append(name)
        if label:
            self._custom_tools[name] = label
        return self

    def placeholder(self, text: str) -> Self:
        """Ghost text shown while the editor is empty."""
        self._placeholder = text
        return self

    def merge_tags(self, tags: Sequence[str]) -> Self:
        """Insertable placeholders such as ``{{ customer_name }}``."""
        self._merge_tags = [str(tag) for tag in tags]
        return self

    def get_merge_tags(self) -> list[str]:
        return list(self._merge_tags)

    def min_height(self, value: str | int) -> Self:
        """CSS height for the writing surface (``"18rem"`` or a pixel count)."""
        self._min_height = f"{value}px" if isinstance(value, (int, float)) else value
        return self

    def tool_label(self, name: str) -> str:
        if name in self._custom_tools:
            return self._custom_tools[name]
        if name in RICH_EDITOR_TOOLS:
            return RICH_EDITOR_TOOLS[name]
        return name[:1].upper() + name[1:]

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        val = "" if state is None else str(state)
        is_disabled = self.is_disabled(**ctx) or self._readonly
        disabled = " disabled" if is_disabled else ""
        disabled_attr = ' data-editor-disabled="true"' if is_disabled else ""
        live = " wire:model.live" if self._live else " wire:model"
        toolbar = ",".join(self._toolbar_buttons)
        toolbar_spans = "".join(
            f'<button type="button" class="or-editor-tool" data-tool="{e(b)}" '
            f'aria-label="{e(self.tool_label(b))}" title="{e(self.tool_label(b))}">'
            f"{e(self.tool_label(b))}</button>"
            for b in self._toolbar_buttons
        )
        for tag in self._merge_tags:
            toolbar_spans += (
                f'<button type="button" class="or-editor-tool or-editor-merge-tag" '
                f'data-tool="mergeTag:{e(tag)}" title="Insert {e(tag)}">{{{{ {e(tag)} }}}}</button>'
            )
        placeholder_attr = (
            f' data-placeholder="{e(self._placeholder)}"' if self._placeholder else ""
        )
        height = f' style="min-height: {e(self._min_height)}"' if self._min_height else ""
        helper = self._helper_html(**ctx)
        return (
            f'<div class="or-field or-field-RichEditor" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<div class="or-editor-toolbar" data-toolbar="{e(toolbar)}">{toolbar_spans}</div>'
            f'<div class="or-editor or-editor-rich" id="or-{name}-editor" data-tiptap '
            f'data-toolbar="{e(toolbar)}" data-input="or-{name}"'
            f"{placeholder_attr}{disabled_attr}{height}{disabled}></div>"
            f'<input type="hidden" class="or-editor-input" id="or-{name}" name="{name}" '
            f'value="{e(val)}"{live}="{name}" data-tiptap-input />{helper}</div>'
        )


class MarkdownEditor(Textarea):
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        return html.replace("or-field-Textarea", "or-field-MarkdownEditor").replace(
            "or-textarea", "or-textarea or-editor or-editor-markdown"
        )


class KeyValue(Field):
    """Editable dictionary — a list of key/value rows the host keeps in sync."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._key_label = "Key"
        self._value_label = "Value"
        self._key_placeholder = "Key"
        self._value_placeholder = "Value"
        self._add_action_label = "Add row"
        self._editable_keys = True
        self._addable = True
        self._deletable = True
        self._reorderable = False

    def key_label(self, text: str) -> Self:
        self._key_label = text
        return self

    def value_label(self, text: str) -> Self:
        self._value_label = text
        return self

    def key_placeholder(self, text: str) -> Self:
        self._key_placeholder = text
        return self

    def value_placeholder(self, text: str) -> Self:
        self._value_placeholder = text
        return self

    def add_action_label(self, text: str) -> Self:
        self._add_action_label = text
        return self

    def editable_keys(self, condition: bool = True) -> Self:
        """Allow (or lock) renaming of keys."""
        self._editable_keys = bool(condition)
        return self

    def addable(self, condition: bool = True) -> Self:
        self._addable = bool(condition)
        return self

    def deletable(self, condition: bool = True) -> Self:
        self._deletable = bool(condition)
        return self

    def reorderable(self, condition: bool = True) -> Self:
        self._reorderable = bool(condition)
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        data = state if isinstance(state, dict) else {}
        locked = self.is_disabled(**ctx) or self._readonly
        disabled = " disabled" if locked else ""
        rows = []
        for i, (key, value) in enumerate(data.items()):
            key_attrs = (
                f'wire:change="setKeyValueKey(\'{name}\', \'{e(key)}\', $event.target.value)"'
                if self._editable_keys and not locked
                else "readonly"
            )
            delete_button = (
                '<button type="button" class="or-key-value-remove or-btn or-btn-gray or-btn-sm" '
                f"wire:click=\"removeKeyValueRow('{name}', '{e(key)}')\" "
                'aria-label="Remove row">&times;</button>'
                if self._deletable and not locked
                else ""
            )
            rows.append(
                f'<div class="or-key-value-row" data-index="{i}" data-key="{e(key)}">'
                f'<input class="or-input or-key-value-key" name="{name}_key_{i}" value="{e(key)}" '
                f'placeholder="{e(self._key_placeholder)}" aria-label="{e(self._key_label)}" '
                f"{key_attrs}{disabled} />"
                f'<input class="or-input or-key-value-value" name="{name}_val_{i}" value="{e(value)}" '
                f'placeholder="{e(self._value_placeholder)}" aria-label="{e(self._value_label)}" '
                f'wire:model="{name}.{e(key)}"{disabled} />'
                f"{delete_button}</div>"
            )
        if not rows:
            rows.append(
                '<div class="or-key-value-row or-key-value-empty">'
                f'<input class="or-input or-key-value-key" placeholder="{e(self._key_placeholder)}" '
                f'aria-label="{e(self._key_label)}"{disabled} />'
                f'<input class="or-input or-key-value-value" placeholder="{e(self._value_placeholder)}" '
                f'aria-label="{e(self._value_label)}"{disabled} /></div>'
            )
        spacer = (
            '<span class="or-key-value-head-spacer" aria-hidden="true"></span>'
            if self._deletable and not locked
            else ""
        )
        header = (
            '<div class="or-key-value-head">'
            f"<span>{e(self._key_label)}</span><span>{e(self._value_label)}</span>"
            f"{spacer}</div>"
        )
        add_button = (
            '<button type="button" class="or-btn or-btn-gray or-btn-sm" '
            f"wire:click=\"addKeyValueRow('{name}')\">{e(self._add_action_label)}</button>"
            if self._addable and not locked
            else ""
        )
        reorder = ' data-reorderable="true"' if self._reorderable else ""
        return (
            f'<div class="or-field or-field-KeyValue" data-field="{name}"{reorder}>'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-key-value-editor">{header}{"".join(rows)}</div>'
            f"{add_button}{self._helper_html(**ctx)}</div>"
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
        self._options_using: Callable[..., Mapping[Any, Any]] | None = None

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

    def options_using(self, callback: Callable[..., Mapping[Any, Any]]) -> Self:
        """Load the record options for the selected type on the server.

        Called as ``callback(type=..., search=...)`` whenever the type changes or
        the operator types in the search box.
        """
        self._options_using = callback
        return self

    def get_options_for_type(self, morph_type: str, search: str = "") -> dict[Any, Any]:
        """Options for one morph type, through ``options_using`` when set."""
        callback = self._options_using
        if callback is None:
            return {}
        result = callback(type=morph_type, search=search)
        return dict(result or {})

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

        # ID select: server-loaded options for the type, then static, then inherited.
        search = str((ctx.get("morph_search") or {}).get(self.get_state_path() or "", ""))
        id_opts = self.get_options_for_type(str(type_value or ""), search)
        if not id_opts:
            id_opts = id_options_by_type.get(str(type_value or ""), {})
        if not id_opts:
            id_opts = self.get_options(**ctx)
        if search:
            needle = search.casefold()
            id_opts = {k: v for k, v in id_opts.items() if needle in str(v).casefold()}
        id_opts_html = []
        for k, v in id_opts.items():
            sel = " selected" if id_value is not None and str(k) == str(id_value) else ""
            id_opts_html.append(f'<option value="{e(k)}"{sel}>{e(v)}</option>')

        searchable_attr = " data-searchable" if self._searchable else ""
        search_box = ""
        if self._searchable:
            search_box = (
                '<input type="search" class="or-input or-morph-search" '
                f'placeholder="Search…" value="{e(search)}" data-morph-search '
                f"wire:model.live.debounce.300ms=\"morph_search.{name}\" "
                f"wire:keydown.debounce.300ms=\"searchMorphOptions('{name}', $event.target.value)\""
                f"{disabled} />"
            )
        return (
            f'<div class="or-field or-field-MorphToSelect" data-field="{name}"{searchable_attr} '
            f'x-data="orbitMorphToSelect">'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-morph-to-select">'
            f'<select class="or-select or-select-morph or-select-morph-type" '
            f'name="{type_name}" data-morph-type{disabled}{live}="{type_name}" '
            f"wire:change=\"setMorphType('{name}', $event.target.value)\">"
            f'{"".join(type_opts_html)}</select>'
            f"{search_box}"
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
    """Pick a record from a table shown in a modal."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._table: Any = None
        self._records: Any = None
        self._modal_heading: str | None = None
        self._browse_label = "Browse"
        self._title_attribute = "name"

    def table(self, table: Any) -> Self:
        """Table rendered inside the picker."""
        self._table = table
        return self

    def get_table(self) -> Any:
        return self._table

    def records(self, records: Any) -> Self:
        """Rows offered in the picker (list or callable)."""
        self._records = records
        return self

    def get_records(self, **ctx: Any) -> list[Any]:
        records = self._records
        if callable(records):
            records = records(**ctx)
        return list(records or [])

    def modal_heading(self, text: str) -> Self:
        self._modal_heading = text
        return self

    def browse_label(self, text: str) -> Self:
        self._browse_label = text
        return self

    def title_attribute(self, name: str) -> Self:
        """Attribute shown in the input once a record is chosen."""
        self._title_attribute = name
        return self

    def get_display_value(self, state: Any, **ctx: Any) -> str:
        """Label for the current value, resolved through options or the record list."""
        if state in (None, ""):
            return ""
        options = self.get_options(**ctx)
        if state in options:
            return str(options[state])
        for record in self.get_records(**ctx):
            value = record.get("id") if isinstance(record, Mapping) else getattr(record, "id", None)
            if str(value) == str(state):
                if isinstance(record, Mapping):
                    return str(record.get(self._title_attribute, state))
                return str(getattr(record, self._title_attribute, state))
        return str(state)

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        display = e(self.get_display_value(state, **ctx))
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        open_field = str((ctx.get("table_select") or {}).get("field") or "")
        modal = ""
        if open_field and open_field == (self.get_state_path() or ""):
            modal = self._render_modal(name, **ctx)
        return (
            f'<div class="or-field or-field-ModalTableSelect" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<div class="or-modal-table-select">'
            f'<input class="or-input" id="or-{name}" name="{name}" value="{display}" '
            f'readonly data-display-value />'
            f'<input type="hidden" data-value wire:model="{name}" value="{e(state or "")}" />'
            f'<button type="button" class="or-btn or-btn-gray"{disabled} '
            f'wire:click="mountTableSelect(\'{name}\')">{e(self._browse_label)}</button>'
            f"</div>{modal}{self._helper_html(**ctx)}</div>"
        )

    def _render_modal(self, name: str, **ctx: Any) -> str:
        heading = self._modal_heading or f"Select {self.get_label(**ctx)}"
        search = str((ctx.get("table_select") or {}).get("search") or "")
        rows = self.get_records(**ctx)
        if search:
            needle = search.casefold()
            rows = [row for row in rows if needle in str(row).casefold()]
        body = self._render_rows(name, rows)
        return (
            '<div class="or-modal-backdrop or-table-select-modal" role="dialog" aria-modal="true">'
            f'<div class="or-modal"><header class="or-modal-header">'
            f'<h2 class="or-modal-heading">{e(heading)}</h2>'
            '<button type="button" class="or-modal-close" wire:click="closeTableSelect()" '
            'aria-label="Close">&times;</button></header>'
            '<div class="or-modal-body">'
            f'<input type="search" class="or-input" placeholder="Search…" value="{e(search)}" '
            f"wire:keydown.debounce.300ms=\"setTableSelectSearch('{name}', $event.target.value)\" />"
            f"{body}</div></div></div>"
        )

    def _render_rows(self, name: str, rows: list[Any]) -> str:
        table = self.get_table()
        if table is not None:
            table.records(rows)
            return table.render(skip_header_actions=True)
        if not rows:
            return '<p class="or-muted">No records.</p>'
        items = []
        for row in rows:
            if isinstance(row, Mapping):
                value = row.get("id", "")
                title = row.get(self._title_attribute, value)
            else:
                value = getattr(row, "id", "")
                title = getattr(row, self._title_attribute, value)
            items.append(
                '<button type="button" class="or-table-select-row" '
                f"wire:click=\"selectTableRecord('{name}', '{e(value)}')\">{e(title)}</button>"
            )
        return f'<div class="or-table-select-rows">{"".join(items)}</div>'
