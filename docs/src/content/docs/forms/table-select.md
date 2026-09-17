---
title: Table select
description: Orbit TableSelect — Select subclass styled for table-backed picking.
---

Select that hints at a tabular picker — still options under the hood.

## Standalone

```python
from almasix.orbit.forms import Form, TableSelect

form = Form.make("demo").schema([
        TableSelect.make("post_id")
            .options({"1": "Shipping Orbit docs", "2": "Panel brand colors"})
            .searchable()
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, TableSelect

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            TableSelect.make("user_id")
                .options(lambda **ctx: ctx.get("users", {}))
                .required(),
        ])
```

## Key methods

- `Inherits Select`
- `Adds `or-select-table``
- `.options(...) / .searchable() / .required()`
- `.disabled(...) / .visible(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).


## Preview

![Orbit forms/select (light)](/examples/light/forms/select.png)

![Orbit forms/select (dark)](/examples/dark/forms/select.png)
