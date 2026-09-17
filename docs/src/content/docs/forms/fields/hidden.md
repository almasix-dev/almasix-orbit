---
title: Hidden
description: Orbit Hidden field — no label, just wire:model state.
---

State without chrome — IDs, tokens, and secrets the UI shouldn’t stare at.

## Standalone

```python
from almasix.orbit.forms import Form, Hidden

form = Form.make("demo").schema([
        Hidden.make("tenant_id").default("acme")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Hidden

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Hidden.make("id"),
            Hidden.make("version").default(1),
        ])
```

## Key methods

- `.default(...)`
- `.state_path(...) when the key differs from the name`
- `.dehydrated(False) to keep it out of payloads`
- `No label / helper rendering`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/form.png)

![Orbit form example (dark)](/examples/dark/form.png)

