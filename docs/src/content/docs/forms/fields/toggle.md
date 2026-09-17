---
title: Toggle
description: Orbit Toggle field — boolean switch styled distinctly from Checkbox.
---

Same boolean energy as Checkbox, dressed as a switch.

## Standalone

```python
from almasix.orbit.forms import Form, Toggle

form = Form.make("demo").schema([
        Toggle.make("notifications").label("Email notifications")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Toggle

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Toggle.make("dark_mode").label("Dark mode"),
            Toggle.make("public")
                .disabled(lambda record=None, **_: record and record.get("locked")),
        ])
```

## Key methods

- `.label(...)`
- `.default(...) / .disabled(...) / .visible(...)`
- `.live() for immediate wire updates`
- `Inherits Checkbox behaviour; CSS class is `or-toggle``

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-Toggle" data-field="notifications">
  <label class="or-checkbox-label">
    <input class="or-toggle" type="checkbox" name="notifications" wire:model="notifications" />
    Email notifications
  </label>
</div>
```
