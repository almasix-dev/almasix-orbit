---
title: Tags input
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

![Orbit form example (light)](/examples/light/form.png)

![Orbit form example (dark)](/examples/dark/form.png)

