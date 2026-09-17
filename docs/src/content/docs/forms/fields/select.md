---
title: Select
description: Orbit Select field with options, multiple, searchable, and relationships.
---

Pick one (or many) from a map of options — searchable when the list gets long.

## Standalone

```python
from almasix.orbit.forms import Form, Select

form = Form.make("demo").schema([
        Select.make("status")
            .options({"draft": "Draft", "published": "Published"})
            .searchable()
            .required()
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Select

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Select.make("status")
                .options({"draft": "Draft", "published": "Published"})
                .default("draft"),
            Select.make("author_id")
                .relationship("author", "name")
                .searchable(),
        ])
```

## Key methods

- `.options(dict | callable)`
- `.multiple() / .searchable()`
- `.relationship(name, title_attribute)`
- `.required() / .disabled(...) / .visible(...) / .live()`
- `.default(...) / .label(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-Select" data-field="status">
  <label class="or-label" for="or-status">Status</label>
  <select class="or-select" id="or-status" name="status" wire:model="status">
    <option value="draft" selected>Draft</option>
    <option value="published">Published</option>
  </select>
</div>
```
