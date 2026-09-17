---
title: Repeater
description: Orbit Repeater — nested schema with clone, collapse, reorder, and limits.
---

A list of nested field schemas — line items, speakers, “add another.”

## Standalone

```python
from almasix.orbit.forms import Form, Repeater, TextInput

form = Form.make("demo").schema([
        Repeater.make("links")
            .schema([
                TextInput.make("label").required(),
                TextInput.make("url").url().required(),
            ])
            .cloneable()
            .collapsible()
            .reorderable()
            .item_label(lambda index, **_: f"Link {index + 1}")
            .min_items(1)
            .max_items(5)
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Repeater, TextInput

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Repeater.make("speakers").schema([
                TextInput.make("name").required(),
                TextInput.make("title"),
            ]),
        ])
```

## Key methods

- `.schema([...])` — nested fields / layouts
- `.cloneable()` / `.collapsible()` / `.reorderable()` — item action buttons
- `.item_label(str | callable)` — per-item header
- `.min_items(n)` / `.max_items(n)` — limits (`data-min-items` / `data-max-items`)
- Wire actions: `addRepeaterItem`, `removeRepeaterItem`, `cloneRepeaterItem`, `moveRepeaterItem`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

Import nested fields from `almasix.orbit.forms` as usual.


## Preview

![Orbit forms/repeater (light)](/examples/light/forms/repeater.png)

![Orbit forms/repeater (dark)](/examples/dark/forms/repeater.png)
