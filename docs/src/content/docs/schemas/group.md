---
title: Group
description: Fuse schema children without fieldset chrome — optional column grid for lightweight inline clusters.
---

## Introduction

`Group` fuses child components without fieldset or section chrome. Use it when fields should sit together visually but you don’t want a legend or heading — for example a SKU and quantity pair beside a longer notes field. Optionally enable a column grid with `.columns(n)`.

```python title="app/orbit/schemas/group_basic.py"
from almasix.orbit.schemas import Group
from almasix.orbit.forms import TextInput

Group.make()
    .columns(2)
    .schema([
        TextInput.make("sku"),
        TextInput.make("qty"),
    ])
```

![Basic group (light)](/examples/light/schemas/group/basic.png)
![Basic group (dark)](/examples/dark/schemas/group/basic.png)

## With columns

When `.columns(n)` is set, the group also applies `or-grid or-grid-cols-N` so children lay out like a lightweight [Grid](/schemas/grid/) — still without fieldset chrome:

```python title="app/orbit/schemas/group_columns.py"
Group.make().columns(3).schema([
    TextInput.make("a"),
    TextInput.make("b"),
    TextInput.make("c"),
])
```

## Without columns

Omit `.columns(...)` to render children in a simple fused block (`or-schema-group` only):

```python title="app/orbit/schemas/group_plain.py"
Group.make().schema([
    TextInput.make("prefix"),
    TextInput.make("suffix"),
])
```

## Nesting

Groups nest cleanly inside sections, tabs, and splits — useful for SKU/qty clusters beside longer fields:

```python title="app/orbit/schemas/group_nested.py"
from almasix.orbit.schemas import Section, Group, Split
from almasix.orbit.forms import TextInput, Textarea

Section.make("inventory").heading("Inventory").schema([
    Split.make().from_("md").schema([
        Group.make().columns(2).schema([
            TextInput.make("sku"),
            TextInput.make("qty"),
        ]),
        Textarea.make("notes"),
    ]),
])
```

![Group + split (light)](/examples/light/schemas/group-split.png)
![Group + split (dark)](/examples/dark/schemas/group-split.png)

## API reference

| Method | Role |
|--------|------|
| `.columns` | Optional grid column count |
| `.schema` | Child components |
| `.dense` / `.gap` / `.defer_loading` | Shared layout helpers |

For labeled chrome prefer [Fieldset](/schemas/fieldset/) or [Section](/schemas/sections/). Side-by-side panes that stack: [Split](/schemas/split/).
