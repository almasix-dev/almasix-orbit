---
title: Schemas overview
description: Nest Orbit UI with Schema, layouts, callouts, empty states, and primes — the fabric under forms, infolists, and custom pages.
---

## Introduction

Schemas are the nesting fabric under forms, infolists, and anything else that needs a component tree. A `Schema` holds state, dehydrates fields, and renders children. Layouts organize fields; primes, callouts, and empty states add non-field chrome.

Orbit’s Python API mirrors Filament 5’s schemas package: compose with `.schema([...])` / `.components([...])`, hydrate with `.state()` / `.fill()`, read back with `.get_state()` / `.dehydrate()`, and render HTML for Conduit hosts.

## Available components

### Form fields

Form fields live under [`almasix.orbit.forms`](/forms/overview/) — text inputs, selects, toggles, repeaters, and more. Nest them inside any layout or top-level schema.

### Infolist entries

Read-only entry components live under [infolists](/infolists/overview/). They share the same schema nesting model as forms.

### Layout components

| Component | Role |
|-----------|------|
| [Grid](/schemas/grid/) | Fixed column count |
| [Flex](/schemas/flex/) | Flex row that stacks below a breakpoint |
| [Group](/schemas/group/) | Fuse children without fieldset chrome |
| [Split](/schemas/split/) | Side-by-side panes that stack |
| [Fieldset](/schemas/fieldset/) | Native `<fieldset>` + legend |
| [Section](/schemas/sections/) | Heading, icon, collapsible / aside / compact |
| [Tabs](/schemas/tabs/) | Horizontal panels with icons and badges |
| [Wizard](/schemas/wizards/) | Multi-step nav with continue / back / skip |

See also the [layouts](/schemas/layouts/) gallery.

### Prime components

[Primes](/schemas/primes/) are read-only display pieces — `Text`, `Icon`, `Image`, and `UnorderedList` — for infolists and inline form summaries.

### Other schema components

| Component | Role |
|-----------|------|
| [Callout](/schemas/callouts/) | Info / success / warning / danger banners |
| [Empty state](/schemas/empty-states/) | Zero-data placeholders with optional actions |

## An example schema

```python title="app/orbit/schemas/user_profile.py"
from almasix.orbit.schemas import Schema, Grid, Section
from almasix.orbit.forms import TextInput, Select, Toggle

Schema.make("user")
    .columns(1)
    .schema([
        Section.make("profile")
            .heading("Profile")
            .description("Public details for this account.")
            .icon("heroicon-o-user")
            .schema([
                Grid.make()
                    .columns(2)
                    .schema([
                        TextInput.make("first_name").required(),
                        TextInput.make("last_name").required(),
                        TextInput.make("email").email().column_span(2),
                        Select.make("role").options({
                            "admin": "Admin",
                            "editor": "Editor",
                        }),
                        Toggle.make("active").label("Active"),
                    ]),
            ]),
    ])
```

![Schemas overview (light)](/examples/light/schemas/overview.png)
![Schemas overview (dark)](/examples/dark/schemas/overview.png)

A typical section chrome shot (same nesting idea):

![Section (light)](/examples/light/schemas/section.png)
![Section (dark)](/examples/dark/schemas/section.png)

## Component utility injection

When you pass a callable to a fluent helper (visibility, labels, prime content, dehydrate mutators, and similar), Orbit’s `evaluate()` injects only the kwargs the callable declares. Common utilities:

| Utility | Meaning |
|---------|---------|
| `state` | Current field / component state (or the schema state bag, depending on call site) |
| `record` | Bound record when rendering against a model / dict row |
| `operation` | Create / edit / view context from `.operation(...)` |
| `component` | The component instance being evaluated |

```python title="app/orbit/schemas/conditional.py"
TextInput.make("publisher")
    .visible(lambda operation=None, **_: operation == "edit")

Text.make()
    .content(lambda state=None, record=None, **_: record.get("title") if record else state)
```

Set the operation on the schema (or pass it through render context):

```python title="app/orbit/schemas/edit_user.py"
Schema.make("user").operation("edit").schema([...])
# schema.get_operation() → "edit"
```

## Deferring loading

Mark a schema (or a layout) so hosts can load chrome asynchronously — emits `data-defer="true"`:

```python title="app/orbit/schemas/heavy.py"
Schema.make("dashboard").defer_loading().schema([...])

Grid.make().defer_loading().columns(3).schema([...])
```

## Global settings

Register defaults for every schema (e.g. in a provider boot hook):

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit.schemas import Schema

Schema.configure_using(lambda schema: schema.columns(1))
```

Callbacks run inside `Schema.make(...)` before your local fluent chain.

## Schema basics

| Method | Role |
|--------|------|
| `.components` / `.schema` | Set the child tree |
| `.columns` | Hint for grid-ish outer chrome (`or-schema-cols-N`) |
| `.state` | Replace the hydrated state dict |
| `.fill` | Merge keys into the state dict |
| `.get_state` | Read the current state bag |
| `.dehydrate` | Collect dehydrated field values (walks nested layouts) |
| `.render` | Return HTML for the tree |
| `.operation` / `.get_operation` | Create / edit / view context |
| `.defer_loading` | Mark for deferred client load |
| `.configure_using` | Class-level default configurator |

```python title="app/orbit/schemas/hydrate.py"
schema = Schema.make("post").schema([TextInput.make("title")])
schema.fill({"title": "Hello"})
schema.get_state()   # {"title": "Hello"}
schema.dehydrate()   # {"title": "Hello"}
```

## Layout gallery

| Page | What you’ll find |
|------|------------------|
| [Layouts](/schemas/layouts/) | Shared layout APIs and composition patterns |
| [Grid](/schemas/grid/) | `.columns`, `.grid_container`, dense / gap |
| [Flex](/schemas/flex/) | `.grow`, `.from_breakpoint` |
| [Group](/schemas/group/) | Chrome-free fuse + optional columns |
| [Split](/schemas/split/) | `.from_breakpoint` / `.from_` |
| [Fieldset](/schemas/fieldset/) | Legend grouping; `.contained(False)` for bare |
| [Sections](/schemas/sections/) | Heading, collapse, aside, compact, persist |
| [Tabs](/schemas/tabs/) | Icons, badges, `.persist_tab`, `.active_tab` |
| [Wizards](/schemas/wizards/) | Steps, skippable, start step |
| [Callouts](/schemas/callouts/) | Status helpers + footer actions |
| [Empty states](/schemas/empty-states/) | Heading, icon, actions |
| [Primes](/schemas/primes/) | Text, icon, image, unordered list |
