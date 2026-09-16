
"""Form fields — Filament-familiar fluent API."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Self

from almasix.orbit.support.component import Component
from almasix.orbit.support.html import e


class Field(Component):
    """Base form field."""

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._rules: list[str | Callable[..., Any]] = []
        self._required = False
        self._placeholder: str | None = None
        self._autocomplete: str | None = None
        self._options: dict[Any, Any] | Callable[..., dict[Any, Any]] = {}
        self._multiple = False
        self._searchable = False
        self._relationship: tuple[str, str] | None = None
        self._input_type = "text"
        self._rows: int | None = None
        self._accepted_file_types: list[str] = []
        self._max_size: int | None = None

    def rules(self, *rules: str | Callable[..., Any]) -> Self:
        self._rules.extend(rules)
        return self

    def get_rules(self) -> list[str | Callable[..., Any]]:
        rules = list(self._rules)
        if self._required and "required" not in rules:
            rules.insert(0, "required")
        return rules

    def required(self, condition: bool = True) -> Self:
        self._required = condition
        return self

    def is_required(self) -> bool:
        return self._required

    def placeholder(self, text: str) -> Self:
        self._placeholder = text
        return self

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
            "required": self._required,
            "rules": [r if isinstance(r, str) else getattr(r, "__name__", "callable") for r in self._rules],
            "placeholder": self._placeholder,
            "input_type": self._input_type,
            "multiple": self._multiple,
            "searchable": self._searchable,
            "relationship": self._relationship,
            "options": self.get_options() if not callable(self._options) else {},
        })
        return d

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label())
        req = ' <span class="or-required">*</span>' if self._required else ""
        ph = f' placeholder="{e(self._placeholder)}"' if self._placeholder else ""
        disabled = " disabled" if self.is_disabled(**ctx) else ""
        val = "" if state is None else e(str(state))
        live = ' wire:model.live' if self._live else ' wire:model'
        helper = f'<p class="or-helper">{e(self._helper_text)}</p>' if self._helper_text else ""
        return (
            f'<div class="or-field or-field-{type(self).__name__}" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}{req}</label>'
            f'<input class="or-input" id="or-{name}" name="{name}" type="{e(self._input_type)}" '
            f'value="{val}"{ph}{disabled}{live}="{name}" />{helper}</div>'
        )


class TextInput(Field):
    pass


class Textarea(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label())
        rows = self._rows or 4
        val = "" if state is None else e(str(state))
        disabled = " disabled" if self.is_disabled(**ctx) else ""
        live = ' wire:model.live' if self._live else ' wire:model'
        return (
            f'<div class="or-field or-field-Textarea" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<textarea class="or-textarea" id="or-{name}" name="{name}" rows="{rows}"'
            f'{disabled}{live}="{name}">{val}</textarea></div>'
        )


class Select(Field):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label())
        opts = []
        for k, v in self.get_options(**ctx).items():
            sel = " selected" if str(k) == str(state) else ""
            opts.append(f'<option value="{e(k)}"{sel}>{e(v)}</option>')
        multi = " multiple" if self._multiple else ""
        disabled = " disabled" if self.is_disabled(**ctx) else ""
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
        label = e(self.get_label())
        checked = " checked" if state else ""
        disabled = " disabled" if self.is_disabled(**ctx) else ""
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
        label = e(self.get_label())
        accept = ",".join(self._accepted_file_types)
        acc = f' accept="{e(accept)}"' if accept else ""
        return (
            f'<div class="or-field or-field-FileUpload" data-field="{name}">'
            f'<label class="or-label" for="or-{name}">{label}</label>'
            f'<input class="or-file" id="or-{name}" type="file" name="{name}"{acc} '
            f'wire:model="{name}" /></div>'
        )


class Radio(Select):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label())
        opts = []
        for k, v in self.get_options(**ctx).items():
            checked = " checked" if str(k) == str(state) else ""
            opts.append(
                f'<label class="or-radio-label"><input type="radio" class="or-radio" '
                f'name="{name}" value="{e(k)}" wire:model="{name}"{checked} /> {e(v)}</label>'
            )
        return (
            f'<div class="or-field or-field-Radio" data-field="{name}" role="radiogroup" '
            f'aria-label="{label}"><span class="or-label">{label}</span>{"".join(opts)}</div>'
        )


class CheckboxList(Select):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._multiple = True


class TagsInput(Field):
    pass


class ColorPicker(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "color"


class RichEditor(Textarea):
    pass


class MarkdownEditor(Textarea):
    pass


class KeyValue(Field):
    pass


class Repeater(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._schema: list[Component] = []

    def schema(self, components: Sequence[Component]) -> Self:
        self._schema = list(components)
        return self

    def get_schema(self) -> list[Component]:
        return list(self._schema)


class Builder(Repeater):
    pass


class Slider(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._input_type = "range"


class ToggleButtons(Select):
    pass


class CodeEditor(Textarea):
    pass


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
    pass


class MorphToSelect(Select):
    pass


class TableSelect(Select):
    pass


class ModalTableSelect(Select):
    pass


class RelationshipRepeater(Repeater):
    pass
