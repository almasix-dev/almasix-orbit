---
title: Repeater
description: Orbit Repeater — nested schema with add/remove item actions.
---

A list of nested field schemas — line items, speakers, “add another.”

## Standalone

```python
from almasix.orbit.forms import Form, Repeater, TextInput, Textarea, Select

form = Form.make("demo").schema([
        Repeater.make("links").schema([
            TextInput.make("label").required(),
            TextInput.make("url").url().required(),
        ])
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Repeater, TextInput, Textarea, Select

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Repeater.make("speakers").schema([
                TextInput.make("name").required(),
                TextInput.make("title"),
            ]),
        ])
```

## Key methods

- `.schema([...]) — nested fields / layouts`
- `.get_schema() / .label(...)`
- `.disabled(...) / .visible(...)`
- `Renders Add / Remove with `addRepeaterItem` / `removeRepeaterItem``

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).


Import nested fields from `almasix.orbit.forms` as usual.


## Preview

```html
<div class="or-field or-field-Repeater" data-field="links">
  <span class="or-label">Links</span>
  <div class="or-repeater">
    <div class="or-repeater-item" data-index="0">
      <div class="or-repeater-item-body">
        <div class="or-field or-field-TextInput" data-field="label">…</div>
      </div>
      <button type="button" class="or-btn or-btn-danger or-btn-sm" wire:click="removeRepeaterItem('links', 0)">Remove</button>
    </div>
  </div>
  <button type="button" class="or-btn or-btn-gray or-btn-sm" wire:click="addRepeaterItem('links')">Add item</button>
</div>
```
