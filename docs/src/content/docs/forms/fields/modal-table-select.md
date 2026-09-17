---
title: ModalTableSelect
description: Orbit ModalTableSelect — browse records via mountTableSelect.
---

Readonly display + Browse button that mounts a table picker modal.

## Standalone

```python
from almasix.orbit.forms import Form, ModalTableSelect

form = Form.make("demo").schema([
        ModalTableSelect.make("post_id").label("Post")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, ModalTableSelect

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            ModalTableSelect.make("assignee_id")
                .label("Assignee")
                .required(),
        ])
```

## Key methods

- `.label(...) / .required(...)`
- `.disabled(...) / .visible(...)`
- `Renders readonly input + Browse (`wire:click="mountTableSelect(...)")``
- `State is the selected id/display value you wire in`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-ModalTableSelect" data-field="post_id">
  <label class="or-label" for="or-post_id">Post</label>
  <div class="or-modal-table-select">
    <input class="or-input" id="or-post_id" name="post_id" value="Shipping Orbit docs" readonly wire:model="post_id" />
    <button type="button" class="or-btn or-btn-gray" wire:click="mountTableSelect('post_id')">Browse</button>
  </div>
</div>
```
