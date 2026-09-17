---
title: MorphToSelect
description: Orbit MorphToSelect — Select subclass for polymorphic targets.
---

Select-shaped picker for morph-style relations — type + id vibes.

## Standalone

```python
from almasix.orbit.forms import Form, MorphToSelect

form = Form.make("demo").schema([
        MorphToSelect.make("notable")
            .options({"post:1": "Post #1", "user:2": "User #2"})
            .searchable()
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, MorphToSelect

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            MorphToSelect.make("subject")
                .options(lambda **ctx: ctx.get("morph_options", {}))
                .searchable()
                .required(),
        ])
```

## Key methods

- `Inherits Select (`.options`, `.searchable`, `.multiple`)`
- `Adds `or-select-morph` class`
- `.required() / .disabled(...) / .visible(...)`
- `.relationship(...) when you resolve titles yourself`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-MorphToSelect" data-field="notable">
  <label class="or-label" for="or-notable">Notable</label>
  <select class="or-select or-select-morph" id="or-notable" name="notable" wire:model="notable">
    <option value="post:1">Post #1</option>
  </select>
</div>
```
