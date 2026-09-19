---
title: Layouts
description: Structure schemas with Grid, Flex, Group, Split, Fieldset, Section, Tabs, and Wizard — shared dense, gap, and defer APIs.
---

## Introduction

Layout components from `almasix.orbit.schemas` nest inside any schema — forms, infolists, and custom pages. Prefer `Section` for titled panels, `Tabs` / `Wizard` for progressive disclosure, and `Grid` / `Flex` / `Group` / `Split` for alignment without extra chrome.

```python title="app/orbit/schemas/layout_compose.py"
from almasix.orbit.schemas import Flex, Group, Split, Section, Fieldset
from almasix.orbit.forms import TextInput

Section.make("profile").heading("Profile").collapsible().schema([
    Flex.make().from_breakpoint("md").schema([
        TextInput.make("first_name"),
        TextInput.make("last_name"),
    ]),
    Group.make().columns(2).schema([
        TextInput.make("city"),
        TextInput.make("country"),
    ]),
    Split.make().from_("lg").schema([
        Fieldset.make().label("Contact").schema([TextInput.make("email")]),
        Fieldset.make().label("Notes").schema([TextInput.make("notes")]),
    ]),
])
```

![Grid + flex (light)](/examples/light/schemas/grid-flex.png)
![Grid + flex (dark)](/examples/dark/schemas/grid-flex.png)

## Shared layout APIs

Every layout inherits from `Layout`:

| Method | Role |
|--------|------|
| `.schema` | Nested child components |
| `.dense` | Tighter spacing (`or-dense`) |
| `.gap` | `True` (default), `False` (none), or a named gap token string |
| `.defer_loading` | Emit `data-defer` for async chrome |

```python title="app/orbit/schemas/layout_shared.py"
Grid.make().dense().gap(False).columns(2).schema([...])
Flex.make().gap("sm").from_breakpoint("md").schema([...])
```

## Component map

| Component | Role |
|-----------|------|
| [Grid](/schemas/grid/) | Responsive columns, dense / gap, grid container |
| [Flex](/schemas/flex/) | Flex row with breakpoint stacking |
| [Group](/schemas/group/) | Fuse children (optional columns) |
| [Split](/schemas/split/) | Side-by-side panes that stack |
| [Section](/schemas/sections/) | Heading, icon, compact / aside, collapsible |
| [Fieldset](/schemas/fieldset/) | Native fieldset + legend; optional bare mode |
| [Tabs](/schemas/tabs/) | Icons, badges, persist |
| [Wizard](/schemas/wizards/) | Nav, continue / back, skip |

## More layout shots

![Group + split (light)](/examples/light/schemas/group-split.png)
![Group + split (dark)](/examples/dark/schemas/group-split.png)

![Fieldset (light)](/examples/light/schemas/fieldset.png)
![Fieldset (dark)](/examples/dark/schemas/fieldset.png)
