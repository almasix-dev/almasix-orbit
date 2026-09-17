---
title: Forms
description: Build Orbit forms with fields, validation, and schema layouts.
---

Forms are fluent field trees. You describe the shape; Orbit handles state, dehydration, and HTML.

```python
from almasix.orbit.forms import Form, TextInput, Textarea, Select
from almasix.orbit.schemas import Section

form = Form.make("post").schema([
    Section.make("basics")
    .heading("Basics")
    .description("Title and routing.")
    .schema([
        TextInput.make("title").required().max_length(200),
        TextInput.make("slug").required().helper_text("Used in URLs"),
        Select.make("status")
            .options({"draft": "Draft", "published": "Published"})
            .searchable(),
        Textarea.make("body").rows(10),
    ]),
])

errors = form.validate({"title": ""})
# {"title": ["…"]}
```

`Form` extends `Schema` — you get `.state()`, `.fill()`, `.dehydrate()`, `.columns()`, and `.render()` for free. Prefer `.schema([...])` over `.components([...])`; both work.

## Guides

| Page | What you’ll find |
|------|------------------|
| [Standalone forms](/forms/standalone/) | Forms outside a Resource |
| [Closures](/forms/closures/) | Callable label / options / visible / disabled |
| [Field reference](/forms/fields/text-input/) | Every field type, one page each |

## Field API

Every field starts with `Field.make("name")` (subclasses call the same factory):

```python
TextInput.make("email")
    .label("Email address")
    .placeholder("you@acme.test")
    .helper_text("We never sell this.")
    .hint("Work email preferred")
    .required()
    .email()
    .disabled(False)
    .visible(True)
    .live()                 # wire: live updates
    .dehydrated(True)
    .default("you@acme.test")
    .rules("required", "email")
```

Handy shortcuts: `.email()`, `.password()`, `.numeric()`, `.integer()`, `.tel()`, `.url()`, `.max_length(n)`, `.min_length(n)`, `.rows(n)`, `.options(...)`, `.multiple()`, `.searchable()`, `.relationship(name, title_attribute)`.

Visibility / disabled / options / labels can be callables — see [Closures](/forms/closures/).

## Validation

`form.validate(data)` walks fields and applies **string rules** only (callables in `.rules()` are ignored by the validator today).

| Rule | Meaning |
|------|---------|
| `required` | Non-empty |
| `email` | Looks like an email |
| `numeric` / `integer` | Number-ish |
| `url` | Looks like a URL |
| `min:N` / `max:N` | Length or numeric bounds |

```python
TextInput.make("age").integer().rules("required", "min:18")
```

## Field types

| Field | Page |
|-------|------|
| `TextInput` | [TextInput](/forms/fields/text-input/) |
| `Textarea` | [Textarea](/forms/fields/textarea/) |
| `Select` / `MultiSelect` | [Select](/forms/fields/select/) · [MultiSelect](/forms/fields/multi-select/) |
| `Checkbox` / `Toggle` | [Checkbox](/forms/fields/checkbox/) · [Toggle](/forms/fields/toggle/) |
| `CheckboxList` / `Radio` | [CheckboxList](/forms/fields/checkbox-list/) · [Radio](/forms/fields/radio/) |
| `Hidden` / `Placeholder` | [Hidden](/forms/fields/hidden/) · [Placeholder](/forms/fields/placeholder/) |
| Date / time | [DatePicker](/forms/fields/date-picker/) · [DateTimePicker](/forms/fields/date-time-picker/) · [TimePicker](/forms/fields/time-picker/) |
| `FileUpload` / `ColorPicker` / `Slider` | [FileUpload](/forms/fields/file-upload/) · [ColorPicker](/forms/fields/color-picker/) · [Slider](/forms/fields/slider/) |
| `TagsInput` / `KeyValue` / `ToggleButtons` | [TagsInput](/forms/fields/tags-input/) · [KeyValue](/forms/fields/key-value/) · [ToggleButtons](/forms/fields/toggle-buttons/) |
| Editors | [RichEditor](/forms/fields/rich-editor/) · [MarkdownEditor](/forms/fields/markdown-editor/) · [CodeEditor](/forms/fields/code-editor/) |
| `OneTimeCodeInput` | [OneTimeCodeInput](/forms/fields/one-time-code-input/) |
| Repeaters | [Repeater](/forms/fields/repeater/) · [Builder](/forms/fields/builder/) · [RelationshipRepeater](/forms/fields/relationship-repeater/) |
| `ViewField` | [ViewField](/forms/fields/view-field/) |
| Relation-ish selects | [MorphToSelect](/forms/fields/morph-to-select/) · [TableSelect](/forms/fields/table-select/) · [ModalTableSelect](/forms/fields/modal-table-select/) |

Import them from `almasix.orbit.forms`.

## Layouts inside forms

Nest [schema layouts](/schemas/) — `Section`, `Grid`, `Tabs`, `Fieldset`, `Wizard` — right in the schema list. Fields and layouts mix freely.

```python
from almasix.orbit.schemas import Tabs, Grid

form.schema([
    Tabs.make("profile").tabs(
        ("Account", [
            Grid.make("row").columns(2).schema([
                TextInput.make("first_name").required(),
                TextInput.make("last_name").required(),
            ]),
        ]),
        ("Security", [
            TextInput.make("password").password(),
        ]),
    ),
])
```

## Rendering & state

```python
form.fill({"title": "Hello"})
html = form.render(form.get_state())
payload = form.dehydrate()   # only dehydrated fields with a state path
```

Fields emit `wire:model` attributes so Conduit can sync them when you mount the form inside a live component.

Need the form without a Resource? → [Standalone forms](/forms/standalone/).
