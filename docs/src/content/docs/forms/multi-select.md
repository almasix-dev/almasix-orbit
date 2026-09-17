---
title: Multi-select
description: Orbit MultiSelect — Select with multiple selection enabled by default.
---

A Select that wakes up already multiple — tags, roles, categories, the usual suspects.

## Standalone

```python
from almasix.orbit.forms import Form, MultiSelect

form = Form.make("demo").schema([
        MultiSelect.make("roles")
            .options({"admin": "Admin", "editor": "Editor", "viewer": "Viewer"})
            .searchable()
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, MultiSelect

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            MultiSelect.make("category_ids")
                .options(lambda **ctx: ctx.get("categories", {}))
                .searchable(),
        ])
```

## Key methods

- `.options(dict | callable)`
- `.searchable() — `.multiple()` is already on`
- `.required() / .disabled(...) / .visible(...)`
- `.label(...) / .helper_text(...) / .default([...])`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/forms/overview.png)

![Orbit form example (dark)](/examples/dark/forms/overview.png)

