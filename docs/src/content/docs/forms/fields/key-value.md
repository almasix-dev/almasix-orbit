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

![Orbit form example (light)](/examples/light/form.png)

![Orbit form example (dark)](/examples/dark/form.png)

