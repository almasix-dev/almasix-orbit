---
title: MorphToSelect
description: Orbit MorphToSelect — type toggle plus id select for polymorphic targets.
---

Type + id picker for morph-style relations.

## Standalone

```python
from almasix.orbit.forms import Form, MorphToSelect

form = Form.make("demo").schema([
        MorphToSelect.make("notable")
            .types([
                {"type": "post", "label": "Post", "options": {"1": "Hello"}},
                {"type": "user", "label": "User", "options": {"2": "Ada"}},
            ])
            .searchable()
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, MorphToSelect

class CommentResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            MorphToSelect.make("subject")
                .types(["App\\Models\\Post", "App\\Models\\User"])
                .required(),
        ])
```

## Key methods

- `.types([...])` — class strings or `{type, label, options}` maps
- `.type_attribute(...)` / `.id_attribute(...)` — state keys (defaults `type` / `id`)
- Inherits Select (`.options`, `.searchable`, …)
- Renders type select + id select with `or-select-morph-*` classes

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-MorphToSelect" data-field="notable">
  <span class="or-label">Notable</span>
  <div class="or-morph-to-select">
    <select class="or-select or-select-morph or-select-morph-type">…</select>
    <select class="or-select or-select-morph or-select-morph-id">…</select>
  </div>
</div>
```
