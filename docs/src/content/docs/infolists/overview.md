---
title: Infolists overview
description: Build Filament-familiar read-only record views with Orbit entries — labels, placeholders, copyable state, formatters, and schema layouts.
---

## Introduction

**Infolists** are the show side of a resource — a definition list of typed entries over a record. An `Infolist` is a [`Schema`](/schemas/overview/) specialized for display: compose with `.schema([...])`, nest [Sections](/schemas/sections/) / [Grids](/schemas/grid/), and render with `.render(record)`.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import Infolist, TextEntry, ImageEntry
from almasix.orbit.schemas import Section

Infolist.make("post").schema([
    Section.make("basics").heading("Basics").schema([
        TextEntry.make("title").weight("bold"),
        TextEntry.make("status").badge().color("success"),
        TextEntry.make("slug").copyable(),
        ImageEntry.make("cover").circular(),
    ]),
])
```

![Orbit Infolists overview (light)](/examples/light/infolists/overview.png)

![Orbit Infolists overview (dark)](/examples/dark/infolists/overview.png)

Markup is a `<dl class="or-infolist">` — semantic, styleable, no surprise div soup. Call `.columns(2)` (or `3` / `4`) on the infolist for a multi-column layout.

## Entry types

Every display control is an entry under `almasix.orbit.infolists`. Entries share chrome (label, hint, helper, affixes, placeholders) and resolve state from the record by name (including `author.name` dot paths).

| Entry | Use when |
|-------|----------|
| [Text entry](/infolists/text-entry/) | Default strings, badges, dates, money, markdown |
| [Icon entry](/infolists/icon-entry/) | Icon-forward or boolean check / x |
| [Image entry](/infolists/image-entry/) | Avatars, covers, stacked images |
| [Color entry](/infolists/color-entry/) | Hex / color swatches |
| [Code entry](/infolists/code-entry/) | Monospace / JSON / source |
| [Key-value entry](/infolists/key-value-entry/) | Dict-ish two-column tables |
| [Repeatable entry](/infolists/repeatable-entry/) | Nested entry schema over a list |
| [View entry](/infolists/view-entry/) | Custom HTML escape hatch |

```python title="app/orbit/infolists/post_entries.py"
from almasix.orbit.infolists import TextEntry, IconEntry, ColorEntry

TextEntry.make("title").weight("bold")
IconEntry.make("featured").boolean()
ColorEntry.make("accent").copyable()
```

## On a resource

Wire the builder on the resource; `ViewRecord` renders it automatically.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import Infolist, TextEntry

@classmethod
def infolist(cls, infolist: Infolist) -> Infolist:
    return infolist.schema([
        TextEntry.make("title"),
        TextEntry.make("status").badge(),
    ])
```

Then `PostResource.get_infolist().render(record)` on custom pages, or open the resource view route.

## Setting an entry's label

By default Orbit humanizes the name (`first_name` → `First Name`). Override with `.label(...)` when UI copy should differ from the state key. Callables receive injected utilities such as `record`.

```python title="app/orbit/infolists/labels.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("name")
    .label("Full name")
    .helper_text("Shown on invoices and the public profile.")
    .hint("Legal name")
    .hint_icon("heroicon-m-information-circle")
```

![Orbit Infolist labels (light)](/examples/light/infolists/overview/labels.png)

![Orbit Infolist labels (dark)](/examples/dark/infolists/overview/labels.png)

### Helper text and hints

`.helper_text(...)` sits below the value; `.hint(...)` / `.hint_icon(...)` sit near the label — same chrome pattern as form fields.

```python title="app/orbit/infolists/helper.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("email")
    .label("Email")
    .helper_text("Used for invoices and notifications.")
    .hint("Primary")
    .hint_icon("heroicon-m-envelope")
```

![Orbit Infolist helper + hint (light)](/examples/light/infolists/overview/helper-hint.png)

![Orbit Infolist helper + hint (dark)](/examples/dark/infolists/overview/helper-hint.png)

### Hiding a label

`.hidden_label()` keeps an accessible name while omitting the visible label row.

```python title="app/orbit/infolists/hidden_label.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("title").hidden_label().weight("bold")
```

## Placeholder vs default

`.placeholder(...)` is display-only chrome when state is empty — it does **not** become real state for Image / Color / Icon entries. `.default(...)` fills missing state before formatting (same as form fields).

```python title="app/orbit/infolists/placeholder.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("notes").placeholder("No notes yet")
```

![Orbit Infolist placeholder (light)](/examples/light/infolists/overview/placeholder.png)

![Orbit Infolist placeholder (dark)](/examples/dark/infolists/overview/placeholder.png)

```python title="app/orbit/infolists/default.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("locale").default("en")
```

![Orbit Infolist default (light)](/examples/light/infolists/overview/default.png)

![Orbit Infolist default (dark)](/examples/dark/infolists/overview/default.png)

## Custom state and formatting

`.state(...)` overrides record resolution (static or callable). `.format_state_using(...)` transforms the resolved value before display.

```python title="app/orbit/infolists/format.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("email").format_state_using(lambda state, **_: str(state or "").upper())

TextEntry.make("full_name").state(
    lambda record, **_: f"{record.get('first_name')} {record.get('last_name')}"
)
```

![Orbit Infolist format state (light)](/examples/light/infolists/overview/format-state.png)

![Orbit Infolist format state (dark)](/examples/dark/infolists/overview/format-state.png)

## Copyable state

`.copyable()` wraps the value with a clipboard control. Customize feedback with `.copy_message(...)` and `.copy_message_duration(...)` (milliseconds).

```python title="app/orbit/infolists/copyable.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("slug")
    .copyable()
    .copy_message("Copied!")
    .copy_message_duration(1500)
```

![Orbit Infolist copyable (light)](/examples/light/infolists/overview/copyable.png)

![Orbit Infolist copyable (dark)](/examples/dark/infolists/overview/copyable.png)

## Tooltips and alignment

`.tooltip(...)` sets the `title` on the value cell. Align with `.align_start()` / `.align_center()` / `.align_end()` (or `.alignment("end")`).

```python title="app/orbit/infolists/tooltip.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("status")
    .badge()
    .color("success")
    .tooltip("Visible on the public site")
    .align_end()
```

![Orbit Infolist tooltip (light)](/examples/light/infolists/overview/tooltip.png)

![Orbit Infolist tooltip (dark)](/examples/dark/infolists/overview/tooltip.png)

## Above / below / before / after content

Slot helpers inject HTML around the label or value — Filament’s entry content slots:

| Method | Placement |
|--------|-----------|
| `.above_label` / `.below_label` | Around the `<dt>` |
| `.before_label` / `.after_label` | Inline before / after the label |
| `.above_content` / `.below_content` | Around the `<dd>` |
| `.before_content` / `.after_content` | Inline before / after the value |

```python title="app/orbit/infolists/slots.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("title")
    .above_label('<span class="or-muted">Above label</span>')
    .below_content('<span class="or-muted">Below content</span>')
```

![Orbit Infolist content slots (light)](/examples/light/infolists/overview/slots.png)

![Orbit Infolist content slots (dark)](/examples/dark/infolists/overview/slots.png)

## Affix actions

`.prefix_action(...)` / `.suffix_action(...)` mount named actions beside the value (Conduit `mountAction`).

```python title="app/orbit/infolists/affix.py"
from almasix.orbit.infolists import TextEntry

TextEntry.make("slug").prefix_action("edit").suffix_action("copy")
```

![Orbit Infolist affix actions (light)](/examples/light/infolists/overview/affix.png)

![Orbit Infolist affix actions (dark)](/examples/dark/infolists/overview/affix.png)

## Multi-column layout

```python title="app/orbit/infolists/columns.py"
from almasix.orbit.infolists import Infolist, TextEntry

Infolist.make("post").columns(2).schema([
    TextEntry.make("title"),
    TextEntry.make("status").badge().color("success"),
    TextEntry.make("email"),
    TextEntry.make("slug").copyable(),
])
```

![Orbit Infolist columns (light)](/examples/light/infolists/overview/columns.png)

![Orbit Infolist columns (dark)](/examples/dark/infolists/overview/columns.png)

## Empty infolist → readonly form fallback

Leave `infolist()` empty (or return the untouched builder) and Orbit still gives you a show page. `get_infolist()` notices there are no components and **projects the form schema** into read-only `TextEntry`s:

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.forms import Form, TextInput, Textarea
from almasix.orbit.infolists import Infolist

@classmethod
def form(cls, form: Form) -> Form:
    return form.schema([
        TextInput.make("title").required(),
        TextInput.make("slug").required(),
        Textarea.make("body"),
    ])

@classmethod
def infolist(cls, infolist: Infolist) -> Infolist:
    return infolist  # empty on purpose
```

Under the hood:

1. `get_form().readonly()` — same fields, edit chrome dialed down.
2. Walk nested layouts / repeaters for every `Field`.
3. Emit `TextEntry.make(name).label(field.get_label())` for each.

So create/edit and view stay in sync until you’re ready to hand-craft badges, prose, and copyable slugs. Define an explicit `.schema([...])` whenever the show page should look different from the form — the fallback politely steps aside.

## Shared Entry API cheat sheet

| Method | Notes |
|--------|-------|
| `.label` | Override humanized name |
| `.hidden_label` | Screen-reader-only label |
| `.helper_text` / `.hint` / `.hint_icon` | Chrome under / beside the entry |
| `.placeholder` | Empty-state display (not real state) |
| `.default` | Fallback when state is missing |
| `.state` / `.format_state_using` | Override / transform resolved value |
| `.copyable` / `.copy_message` / `.copy_message_duration` | Clipboard wrapper |
| `.tooltip` | `title` on the value cell |
| `.url` / `.open_url_in_new_tab` | Link the value |
| `.badge` / `.color` / `.icon` / `.icon_position` / `.icon_color` | Text chrome (also on TextEntry) |
| `.align_start` / `.align_center` / `.align_end` | Value alignment |
| `.prefix_action` / `.suffix_action` | Affix mountAction buttons |
| `.above_label` / `.below_content` / … | Content slots |
| `.extra_attributes` / `.extra_entry_wrapper_attributes` | Extra HTML attrs |

Text-specific formatters (money, dates, markdown, lists, …) live on [Text entry](/infolists/text-entry/).
