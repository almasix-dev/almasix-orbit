---
title: TagsInput
description: Orbit TagsInput — chip-style tag editor backed by wire:model.
---

Free-form tags as chips — keywords without pretending they’re a taxonomy.

## Standalone

```python
from almasix.orbit.forms import Form, TagsInput

form = Form.make("demo").schema([
        TagsInput.make("tags")
            .label("Tags")
            .placeholder("Add tag…")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, TagsInput

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            TagsInput.make("keywords").helper_text("Comma-separated works too"),
            TagsInput.make("labels").default(["orbit", "docs"]),
        ])
```

## Key methods

- `State may be a list or a comma-separated string`
- `.label(...) / .placeholder(...) (via input)`
- `.disabled(...) / .visible(...) / .readonly()`
- `.default([...])`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-TagsInput" data-field="tags">
  <label class="or-label" for="or-tags">Tags</label>
  <div class="or-tags">
    <span class="or-tag">orbit</span>
    <span class="or-tag">docs</span>
    <input class="or-input or-tags-input" id="or-tags" name="tags"
           value="orbit,docs" wire:model="tags" placeholder="Add tag…" />
  </div>
</div>
```
