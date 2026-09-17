---
title: ColorPicker
description: Orbit ColorPicker field using native color input.
---

A brand hex, a badge tint, a mood — `type=color` with Orbit chrome.

## Standalone

```python
from almasix.orbit.forms import Form, ColorPicker

form = Form.make("demo").schema([
        ColorPicker.make("brand").label("Brand color").default("#f1511b")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, ColorPicker

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            ColorPicker.make("accent").helper_text("Used in the panel shell"),
            ColorPicker.make("badge_color"),
        ])
```

## Key methods

- `Sets `input_type` to `color``
- `.default("#f1511b")`
- `.label(...) / .helper_text(...)`
- `.disabled(...) / .visible(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-ColorPicker" data-field="brand">
  <label class="or-label" for="or-brand">Brand color</label>
  <input class="or-input" id="or-brand" name="brand" type="color"
         value="#f1511b" wire:model="brand" />
</div>
```
