---
title: Overview
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
| [Standalone forms](/components/form/) | Forms outside a Resource |
| [Closures](/forms/closures/) | Callable label / options / visible / disabled |
| [Field reference](/forms/text-input/) | Every field type, one page each |

## Field API

Every field starts with `Field.make("name")` (subclasses call the same factory):

```python
TextInput.make("email")
    .label("Email address")
    .placeholder("you@acme.test")
    .helper_text("We never sell this.")
    .hint("Work email preferred")
    .prefix("@")
    .suffix(".test")
    .required()
    .email()
    .live(on_blur=True)     # or live(debounce=300)
    .after_state_updated(lambda **_: None)
    .dehydrated(True)
    .default("you@acme.test")
    .rules("required", "email")
```

Handy shortcuts: `.email()`, `.password()`, `.numeric()`, `.integer()`, `.tel()`, `.url()`, `.max_length(n)`, `.min_length(n)`, `.rows(n)`, `.options(...)`, `.enum(MyEnum)`, `.multiple()`, `.searchable()`, `.relationship(name, title_attribute)`, `.unique(...)`, `.exists(...)`, `.regex(...)`, `.between(lo, hi)`.

`Form.validate()` / `Schema.dehydrate()` walk nested layouts (Section / Tabs / Wizard / Repeater schemas).

Visibility / disabled / options / labels can be callables — see [Closures](/forms/closures/).

## Validation

`form.validate(data)` walks **all nested fields** and applies **string rules** and **callable** rules. Use `.validation_attribute()` / `.validation_messages({…})` for friendlier copy. Register DB hooks with `Form.unique_using(...)` / `Form.exists_using(...)` (or pass `unique=` / `exists=` into `validate()`).

| Rule | Meaning |
|------|---------|
| `required` / `filled` / `nullable` | Presence |
| `accepted` / `boolean` / `array` | Type-ish |
| `email` / `url` / `ip` / `uuid` / `json` | Formats |
| `alpha` / `alpha_num` / `alpha_dash` | Character sets |
| `numeric` / `integer` / `digits:N` | Numbers |
| `min:N` / `max:N` / `between:A,B` | Bounds (string length, list size, or numeric) |
| `gt:` / `gte:` / `lt:` / `lte:` | Compare to another field or number |
| `confirmed` / `same:other` / `different:other` | Cross-field |
| `in:a,b` / `not_in:…` | Membership |
| `regex:` / `starts_with:` / `ends_with:` | Pattern |
| `date` / `after:…` / `before:…` | Dates |
| `unique:table,column[,ignore]` / `exists:…` | Pluggable DB checks |
| `mimes:png,jpg` / `distinct` | Files / uniqueness among siblings |
| `unique:table,column` | Via `unique_using` / ctx callback |
| `exists:table,column` | Via `exists_using` / ctx callback |

```python
TextInput.make("age").integer().rules("required", "min:18")
TextInput.make("password").rules("confirmed")
Form.unique_using(lambda value, table=None, column=None, **_: db_is_free(table, column, value))
```

## Field types

| Field | Page |
|-------|------|
| `TextInput` | [TextInput](/forms/text-input/) |
| `Textarea` | [Textarea](/forms/textarea/) |
| `Select` / `MultiSelect` | [Select](/forms/select/) · [MultiSelect](/forms/multi-select/) |
| `Checkbox` / `Toggle` | [Checkbox](/forms/checkbox/) · [Toggle](/forms/toggle/) |
| `CheckboxList` / `Radio` | [CheckboxList](/forms/checkbox-list/) · [Radio](/forms/radio/) |
| `Hidden` / `Placeholder` | [Hidden](/forms/hidden/) · [Placeholder](/forms/placeholder/) |
| Date / time | [DatePicker](/forms/date-picker/) · [DateTimePicker](/forms/date-time-picker/) · [TimePicker](/forms/time-picker/) |
| `FileUpload` / `ColorPicker` / `Slider` | [FileUpload](/forms/file-upload/) · [ColorPicker](/forms/color-picker/) · [Slider](/forms/slider/) |
| `TagsInput` / `KeyValue` / `ToggleButtons` | [TagsInput](/forms/tags-input/) · [KeyValue](/forms/key-value/) · [ToggleButtons](/forms/toggle-buttons/) |
| Editors | [RichEditor](/forms/rich-editor/) · [MarkdownEditor](/forms/markdown-editor/) · [CodeEditor](/forms/code-editor/) |
| `OneTimeCodeInput` | [OneTimeCodeInput](/forms/one-time-code-input/) |
| Repeaters | [Repeater](/forms/repeater/) · [Builder](/forms/builder/) · [RelationshipRepeater](/forms/relationship-repeater/) |
| `ViewField` | [ViewField](/forms/view-field/) |
| Relation-ish selects | [MorphToSelect](/forms/morph-to-select/) · [TableSelect](/forms/table-select/) · [ModalTableSelect](/forms/modal-table-select/) |

Import them from `almasix.orbit.forms`.

## Layouts inside forms

Nest [schema layouts](/schemas/overview/) — `Section`, `Grid`, `Tabs`, `Fieldset`, `Wizard` — right in the schema list. Fields and layouts mix freely.

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

Need the form without a Resource? → [Standalone forms](/components/form/).

## Preview

![Forms overview (light)](/examples/light/forms/overview.png)

![Forms overview (dark)](/examples/dark/forms/overview.png)
