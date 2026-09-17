
"""Form fields — Filament-familiar fluent API."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e


class Field(Component):
    """Base form field."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._rules: list[str | Callable[..., Any]] = []
        self._required: bool | Callable[..., bool] = False
        self._placeholder: str | Callable[..., str] | None = None
        self._autocomplete: str | None = None
        self._options: dict[Any, Any] | Callable[..., dict[Any, Any]] = {}
        self._multiple = False
        self._searchable = False
        self._relationship: tuple[str, str] | None = None
        self._input_type = "text"
        self._rows: int | None = None
        self._accepted_file_types: list[str] = []
        self._max_size: int | None = None
        self._readonly = False

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

    def options(self, options: dict[Any, Any] | Callable[..., dict[Any, Any]]) -> Self:
        self._options = options
        return self

    def get_options(self, **ctx: Any) -> dict[Any, Any]:
        opts = self._options
        return dict(opts(**ctx) if callable(opts) else opts)

    def multiple(self, condition: bool = True) -> Self:
        self._multiple = condition
        return self

    def searchable(self, condition: bool = True) -> Self:
        self._searchable = condition
        return self

    def relationship(self, name: str, title_attribute: str) -> Self:
        self._relationship = (name, title_attribute)
        return self

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
        d.update({
            "required": self._required if not callable(self._required) else None,
            "rules": [r if isinstance(r, str) else getattr(r, "__name__", "callable") for r in self._rules],
            "placeholder": self._placeholder if not callable(self._placeholder) else None,
            "input_type": self._input_type,
            "multiple": self._multiple,
            "searchable": self._searchable,
            "relationship": self._relationship,
            "options": self.get_options() if not callable(self._options) else {},
            "readonly": self._readonly,
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
        live = ' wire:model.live' if self._live else ' wire:model'
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
        live = ' wire:model.live' if self._live else ' wire:model'
        return (
            f'<div class="or-field or-field-Textarea" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<textarea class="or-textarea" id="or-{name}" name="{name}" rows="{rows}"'
            f'{disabled}{readonly}{live}="{name}">{val}</textarea></div>'
        )


class Select(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        opts = []
        for k, v in self.get_options(**ctx).items():
            sel = " selected" if str(k) == str(state) else ""
            opts.append(f'<option value="{e(k)}"{sel}>{e(v)}</option>')
        multi = " multiple" if self._multiple else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        live = ' wire:model.live' if self._live else ' wire:model'
        return (
            f'<div class="or-field or-field-Select" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<select class="or-select" id="or-{name}" name="{name}"{multi}{disabled}'
            f'{live}="{name}">{"".join(opts)}</select></div>'
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
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        accept = ",".join(self._accepted_file_types)
        acc = f' accept="{e(accept)}"' if accept else ""
        disabled = " disabled" if self.is_disabled(**ctx) or self._readonly else ""
        return (
            f'<div class="or-field or-field-FileUpload" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<input class="or-file" id="or-{name}" type="file" name="{name}"{acc}{disabled} '
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
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        return (
            html.replace("or-field-Textarea", "or-field-RichEditor")
            .replace("or-textarea", "or-textarea or-editor or-editor-rich")
            .replace(
                '<label class="or-label"',
                '<div class="or-editor-toolbar" aria-hidden="true">'
                '<span>B</span><span>I</span><span>Link</span></div><label class="or-label"',
                1,
            )
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

    def schema(self, components: Sequence[Component]) -> Self:
        self._schema = list(components)
        return self

    def get_schema(self) -> list[Component]:
        return list(self._schema)

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
            blocks.append(
                f'<div class="or-repeater-item" data-index="{index}">'
                f'<div class="or-repeater-item-body">{"".join(fields)}</div>'
                f'<button type="button" class="or-btn or-btn-danger or-btn-sm" '
                f'wire:click="removeRepeaterItem(\'{name}\', {index})">Remove</button></div>'
            )
        return (
            f'<div class="or-field or-field-Repeater" data-field="{name}" '
            f'x-data="{{ items: {len(items)} }}">'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-repeater">{"".join(blocks)}</div>'
            f'<button type="button" class="or-btn or-btn-gray or-btn-sm" '
            f'wire:click="addRepeaterItem(\'{name}\')">Add item</button></div>'
        )


class Builder(Repeater):
    def render(self, state: Any = None, **ctx: Any) -> str:
        return super().render(state, **ctx).replace("or-field-Repeater", "or-field-Builder")


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
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        return html.replace("or-field-Select", "or-field-MorphToSelect").replace(
            "or-select", "or-select or-select-morph"
        )


class TableSelect(Select):
    def render(self, state: Any = None, **ctx: Any) -> str:
        html = super().render(state, **ctx)
        return html.replace("or-field-Select", "or-field-TableSelect").replace(
            "or-select", "or-select or-select-table"
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
    def render(self, state: Any = None, **ctx: Any) -> str:
        return super().render(state, **ctx).replace("or-field-Repeater", "or-field-RelationshipRepeater")
