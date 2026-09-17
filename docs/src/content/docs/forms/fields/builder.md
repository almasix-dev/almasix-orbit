---
title: Builder
description: Orbit Builder — Repeater subclass for block-oriented nested schemas.
---

A Repeater with Builder branding — block-style nested content.

## Standalone

```python
from almasix.orbit.forms import Form, Builder, TextInput, Textarea, Select

form = Form.make("demo").schema([
        Builder.make("blocks").schema([
            TextInput.make("heading").required(),
            Textarea.make("body").rows(4),
        ])
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Builder, TextInput, Textarea, Select

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Builder.make("sections").schema([
                TextInput.make("title").required(),
                Select.make("type").options({"text": "Text", "gallery": "Gallery"}),
            ]),
        ])
```

## Key methods

- `.schema([...]) — same as Repeater`
- `Render class is `or-field-Builder``
- `.label(...) / .visible(...) / .disabled(...)`
- `Add / Remove wire actions inherited from Repeater`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-Builder" data-field="blocks">
  <span class="or-label">Blocks</span>
  <div class="or-repeater">
    <div class="or-repeater-item" data-index="0">
      <div class="or-repeater-item-body">…</div>
      <button type="button" class="or-btn or-btn-danger or-btn-sm">Remove</button>
    </div>
  </div>
  <button type="button" class="or-btn or-btn-gray or-btn-sm">Add item</button>
</div>
```
