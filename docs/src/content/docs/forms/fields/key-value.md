---
title: KeyValue
description: Orbit KeyValue editor for dictionary-shaped state.
---

Arbitrary key/value rows — metadata bags without inventing columns.

## Standalone

```python
from almasix.orbit.forms import Form, KeyValue

form = Form.make("demo").schema([
        KeyValue.make("meta").label("Metadata")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, KeyValue

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            KeyValue.make("headers").helper_text("Custom response headers"),
            KeyValue.make("meta").default({"env": "prod"}),
        ])
```

## Key methods

- `.label(...) / .helper_text(...)`
- `.default({...}) for seed rows`
- `.disabled(...) / .visible(...)`
- `UI exposes Add row via `wire:click="addKeyValueRow(...)"``

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-KeyValue" data-field="meta">
  <span class="or-label">Metadata</span>
  <div class="or-key-value-editor">
    <div class="or-key-value-row" data-index="0">
      <input class="or-input" name="meta_key_0" value="env" placeholder="Key" />
      <input class="or-input" name="meta_val_0" value="prod" placeholder="Value" wire:model="meta.env" />
    </div>
  </div>
  <button type="button" class="or-btn or-btn-gray or-btn-sm" wire:click="addKeyValueRow('meta')">Add row</button>
</div>
```
