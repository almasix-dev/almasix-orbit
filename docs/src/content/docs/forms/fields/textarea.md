---
title: Textarea
description: Orbit Textarea field for multi-line text input.
---

Multi-line text for bodies, notes, and anything taller than one thought.

## Standalone

```python
from almasix.orbit.forms import Form, Textarea

form = Form.make("demo").schema([
        Textarea.make("body")
            .label("Body")
            .rows(8)
            .placeholder("Write something memorable…")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Textarea

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Textarea.make("body").rows(10).required(),
            Textarea.make("excerpt").rows(3).helper_text("Optional teaser"),
        ])
```

## Key methods

- `.rows(n) — defaults to 4 when unset`
- `.label(...) / .helper_text(...) / .required(...)`
- `.readonly() / .disabled(...) / .visible(...) / .live()`
- `.default(...) / .dehydrated(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-Textarea" data-field="body">
  <label class="or-label" for="or-body">Body</label>
  <textarea class="or-textarea" id="or-body" name="body" rows="8" wire:model="body">Declare once…</textarea>
</div>
```
