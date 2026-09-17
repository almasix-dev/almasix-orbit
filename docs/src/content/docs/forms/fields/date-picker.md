---
title: DatePicker
description: Orbit DatePicker field using native date input.
---

A calendar day via the browser’s native `type=date` control.

## Standalone

```python
from almasix.orbit.forms import Form, DatePicker

form = Form.make("demo").schema([
        DatePicker.make("published_on")
            .label("Publish date")
            .required()
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, DatePicker

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            DatePicker.make("starts_on").required(),
            DatePicker.make("ends_on")
                .visible(lambda record=None, **_: True),
        ])
```

## Key methods

- `Sets `input_type` to `date``
- `.required() / .default("2026-09-17")`
- `.min_length / max rules via `.rules(...)` if needed`
- `.disabled(...) / .visible(...) / .live()`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-DatePicker" data-field="published_on">
  <label class="or-label" for="or-published_on">Publish date <span class="or-required">*</span></label>
  <input class="or-input" id="or-published_on" name="published_on" type="date"
         value="2026-09-17" wire:model="published_on" />
</div>
```
