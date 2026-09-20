---
title: Fieldset
description: Wrap nested fields in semantic fieldset/legend chrome — accessibility-friendly grouping for addresses and payment blocks.
---

## Introduction

`Fieldset` wraps nested fields in a native `<fieldset>` with a `<legend>`. Use it for address blocks, payment details, or any group where semantic grouping matters for accessibility — screen readers announce the legend as the group name.

```python title="app/orbit/schemas/fieldset_basic.py"
from almasix.orbit.schemas import Fieldset
from almasix.orbit.forms import TextInput

Fieldset.make("billing")
    .label("Billing address")
    .schema([
        TextInput.make("line1"),
        TextInput.make("city"),
    ])
```

![Basic fieldset (light)](/examples/light/schemas/fieldset/basic.png)
![Basic fieldset (dark)](/examples/dark/schemas/fieldset/basic.png)

## Contained vs bare

By default the fieldset is **contained** (card-like chrome via `or-fieldset`). Pass `.contained(False)` for a bare fieldset — legend only, with `or-fieldset-bare` and no card shell:

```python title="app/orbit/schemas/fieldset_bare.py"
Fieldset.make("shipping")
    .label("Shipping")
    .contained(False)
    .schema([TextInput.make("line1")])
```

Contained is Orbit’s default; bare is useful inside dense sections where an extra card would feel heavy.

![Fieldset (light)](/examples/light/schemas/fieldset.png)
![Fieldset (dark)](/examples/dark/schemas/fieldset.png)

## Nesting with layouts

Combine fieldsets with [Split](/schemas/split/) or [Grid](/schemas/grid/) for multi-column address UIs:

```python title="app/orbit/schemas/fieldset_split.py"
from almasix.orbit.schemas import Split, Fieldset
from almasix.orbit.forms import TextInput

Split.make().from_("md").schema([
    Fieldset.make().label("Billing").schema([
        TextInput.make("billing_line1"),
        TextInput.make("billing_city"),
    ]),
    Fieldset.make().label("Shipping").schema([
        TextInput.make("shipping_line1"),
        TextInput.make("shipping_city"),
    ]),
])
```

## API reference

| Method | Role |
|--------|------|
| `.label` | Legend text |
| `.contained` | `True` (default) for card chrome; `False` for bare |
| `.schema` | Nested fields |
| `.dense` / `.gap` / `.defer_loading` | Shared layout helpers |

For titled panels with collapse / icon chrome, prefer [Section](/schemas/sections/). For chrome-free fuse, use [Group](/schemas/group/).
