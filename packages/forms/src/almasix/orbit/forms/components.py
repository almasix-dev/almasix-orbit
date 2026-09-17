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

    def options(self, options: Any) -> Self:
        self._options = options
        return self

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
        })
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        req = ' <span class="or-required">*</span>' if self.is_required(**ctx) else ""
        placeholder = self.get_placeholder(**ctx)
        ph = f' placeholder="{e(placeholder)}"' if placeholder else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        readonly = " readonly" if self._readonly else ""
        val = "" if state is None else e(str(state))
        live = " wire:model.live" if self._live else " wire:model"
        helper_text = self.get_helper_text(**ctx)
        helper = f'<p class="or-helper">{e(helper_text)}</p>' if helper_text else ""
        return (
            f'<div class="or-field or-field-{type(self).__name__}" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}{req}</label>'
            f'<input class="or-input" id="or-{name}" name="{name}" type="{e(self._input_type)}" '
            f'value="{val}"{ph}{disabled}{readonly}{live}="{name}" />{helper}</div>'
        )


class TextInput(Field):
    pass


class Textarea(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        rows = self._rows or 4
        val = "" if state is None else e(str(state))
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        readonly = " readonly" if self._readonly else ""
        live = " wire:model.live" if self._live else " wire:model"
        return (
            f'<div class="or-field or-field-Textarea" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<textarea class="or-textarea" id="or-{name}" name="{name}" rows="{rows}"'
            f'{disabled}{readonly}{live}="{name}">{val}</textarea></div>'
        )


class Select(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._create_option_form: Any = None
        self._edit_option_action: str | bool | None = None

    def create_option_form(self, form: Any) -> Self:
        self._create_option_form = form
        return self

    def edit_option_action(self, action: str | bool = True) -> Self:
        self._edit_option_action = action
        return self

    def _render_options_html(self, state: Any, **ctx: Any) -> str:
        selected = state if isinstance(state, (list, tuple, set)) else ([state] if state not in (None, "") else [])
        selected_s = {str(s) for s in selected}
        chunks: list[str] = []
        for group_label, opts in self.get_option_groups(**ctx):
            inner = []
            for k, v in opts.items():
                sel = " selected" if str(k) in selected_s else ""
                label = e(v)
                inner.append(
                    f'<option value="{e(k)}" data-label="{label}"{sel}>{label}</option>'
                )
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
        label = e(self.get_label(**ctx))
        opts_html = self._render_options_html(state, **ctx)
        multi = " multiple" if self._multiple else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        live = " wire:model.live" if self._live else " wire:model"
        searchable_attr = " data-searchable" if self._searchable else ""
        alpine = ' x-data="orbitSearchableSelect"' if self._searchable else ""
        search_input = ""
        if self._searchable:
            search_input = (
                f'<input type="search" class="or-input or-select-search" placeholder="Search…" '
                f'x-model="q" x-on:input="filter()" aria-label="Search {label}" />'
            )
        select_ref = ' x-ref="select"' if self._searchable else ""
        actions = []
        if self._create_option_form is not None:
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
        return (
            f'<div class="or-field or-field-Select" data-field="{name}"{searchable_attr}{rel_attrs}{alpine}>'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f"{search_input}"
            f'<select class="or-select" id="or-{name}" name="{name}"{multi}{disabled}'
            f'{select_ref}{live}="{name}">{opts_html}</select>{actions_html}</div>'
        )


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
            f'name="{name}" wire:model="{name}"{checked}{disabled} /> {label}</label></div>'
        )


class Toggle(Checkbox):
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        return html.replace("or-field-Checkbox", "or-field-Toggle").replace("or-checkbox", "or-toggle")


class Hidden(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        name = e(self.get_state_path() or "")
        val = "" if state is None else e(str(state))
        return f'<input type="hidden" name="{name}" value="{val}" wire:model="{name}" />'


class Placeholder(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._content: str = ""
        self._dehydrated = False

    def content(self, text: str) -> Self:
        self._content = text
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        return f'<div class="or-placeholder"><p class="or-placeholder-content">{e(self._content or state or "")}</p></div>'


class DatePicker(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "date"


class DateTimePicker(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "datetime-local"


class TimePicker(Field):
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

    def disk(self, name: str) -> Self:
        self._disk = name
        return self

    def directory(self, path: str) -> Self:
        self._directory = path
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
        label = e(self.get_label(**ctx))
        accept = ",".join(self._accepted_file_types)
        acc = f' accept="{e(accept)}"' if accept else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        multi = " multiple" if self._multiple else ""
        attrs = []
        if self._disk:
            attrs.append(f'data-disk="{e(self._disk)}"')
        if self._directory:
            attrs.append(f'data-directory="{e(self._directory)}"')
        if self._avatar:
            attrs.append('data-avatar="true"')
        if self._image_preview:
            attrs.append('data-image-preview="true"')
        if self._reorderable:
            attrs.append('data-reorderable="true"')
        if self._max_size is not None:
            attrs.append(f'data-max-size="{self._max_size}"')
        if self._min_size is not None:
            attrs.append(f'data-min-size="{self._min_size}"')
        attr_str = (" " + " ".join(attrs)) if attrs else ""
        avatar_cls = " or-file-avatar" if self._avatar else ""
        preview = ""
        if self._image_preview:
            preview = '<div class="or-file-preview" data-preview-grid aria-live="polite"></div>'
        return (
            f'<div class="or-field or-field-FileUpload{avatar_cls}" data-field="{name}"{attr_str}>'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f"{preview}"
            f'<input class="or-file" id="or-{name}" type="file" name="{name}"{acc}{multi}{disabled} '
            f'wire:model="{name}" /></div>'
        )


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
            opts.append(
                f'<label class="or-radio-label"><input type="radio" class="or-radio" '
                f'name="{name}" value="{e(k)}" wire:model="{name}"{checked}{disabled} /> {e(v)}</label>'
            )
        return (
            f'<div class="or-field or-field-Radio" data-field="{name}" role="radiogroup" '
            f'aria-label="{label}"><span class="or-label">{label}</span>{"".join(opts)}</div>'
        )


class CheckboxList(Select):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._multiple = True

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
            opts.append(
                f'<label class="or-checkbox-label"><input type="checkbox" class="or-checkbox" '
                f'name="{name}" value="{e(k)}" wire:model="{name}"{checked}{disabled} /> {e(v)}</label>'
            )
        return (
            f'<div class="or-field or-field-CheckboxList" data-field="{name}">'
            f'<span class="or-label">{label}</span><div class="or-checkbox-list">{"".join(opts)}</div></div>'
        )


class TagsInput(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        tags = state if isinstance(state, (list, tuple)) else (
            [t.strip() for t in str(state).split(",") if t.strip()] if state else []
        )
        chips = "".join(f'<span class="or-tag">{e(t)}</span>' for t in tags)
        val = e(",".join(str(t) for t in tags))
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        return (
            f'<div class="or-field or-field-TagsInput" data-field="{name}" x-data="{{ tags: \'{val}\' }}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<div class="or-tags">{chips}'
            f'<input class="or-input or-tags-input" id="or-{name}" name="{name}" value="{val}"'
            f'{disabled} wire:model="{name}" placeholder="Add tag…" /></div></div>'
        )


class ColorPicker(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "color"


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

    def schema(self, components: Sequence[Component]) -> Self:
        self._schema = list(components)
        return self

    def get_schema(self) -> list[Component]:
        return list(self._schema)

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

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        items = state if isinstance(state, list) else [{}]
        if not items:
            items = [{}]
        blocks = []
        for index, item in enumerate(items):
            fields = []
            for child in self._schema:
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
        limit_attrs = (" " + " ".join(limits)) if limits else ""
        add_disabled = ""
        if self._max_items is not None and len(items) >= self._max_items:
            add_disabled = " disabled"
        return (
            f'<div class="or-field or-field-Repeater" data-field="{name}"{limit_attrs} '
            f'x-data="{{ items: {len(items)} }}">'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-repeater">{"".join(blocks)}</div>'
            f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
            f'wire:click="addRepeaterItem(\'{name}\')"{add_disabled}>Add item</button></div>'
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

    def blocks(self, blocks: Sequence[Block]) -> Self:
        self._blocks = list(blocks)
        if blocks and not self._schema:
            # Default nested schema from first block for simple renders.
            self._schema = list(blocks[0].get_schema())
        return self

    def get_blocks(self) -> list[Block]:
        return list(self._blocks)

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
        picker = f'<div class="or-builder-picker" role="group">{"".join(picker_btns)}</div>'
        add_btn = (
            f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
            f'wire:click="addRepeaterItem(\'{name}\')"'
        )
        idx = html.find(add_btn)
        if idx >= 0:
            end = html.find("</button>", idx) + len("</button>")
            html = html[:idx] + picker + html[end:]
        elif html.endswith("</div>"):
            html = html[:-6] + picker + "</div>"
        return html


class Slider(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "range"


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
                f'<input type="radio" name="{name}" value="{e(k)}" wire:model="{name}"'
                f'{checked}{disabled} class="or-sr-only" />'
                f"<span>{e(v)}</span></label>"
            )
        return (
            f'<div class="or-field or-field-ToggleButtons" data-field="{name}">'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-toggle-buttons" role="group">{"".join(buttons)}</div></div>'
        )


class CodeEditor(Textarea):
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        return html.replace("or-field-Textarea", "or-field-CodeEditor").replace(
            "or-textarea", "or-textarea or-editor or-editor-code"
        )


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


class RelationshipRepeater(Repeater):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._mutate_relationship_data_before_create: Callable[..., Any] | None = None
        self._mutate_relationship_data_before_fill: Callable[..., Any] | None = None

    def mutate_relationship_data_before_create(self, callback: Callable[..., Any]) -> Self:
        self._mutate_relationship_data_before_create = callback
        return self

    def mutate_relationship_data_before_fill(self, callback: Callable[..., Any]) -> Self:
        self._mutate_relationship_data_before_fill = callback
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        return super().render(state, **ctx).replace("or-field-Repeater", "or-field-RelationshipRepeater")
