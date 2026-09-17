---
title: Radio
description: Orbit Radio field — single-select option group.
---

One choice from a small set — when a Select feels like overkill.

## Standalone

```python
from almasix.orbit.forms import Form, Radio

form = Form.make("demo").schema([
        Radio.make("visibility")
            .options({"public": "Public", "private": "Private"})
            .default("public")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Radio

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Radio.make("priority")
                .options({"low": "Low", "normal": "Normal", "high": "High"})
                .required(),
        ])
```

## Key methods

- `.options(dict | callable)`
- `.default(...) / .required(...)`
- `.disabled(...) / .visible(...) / .label(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/form.png)

![Orbit form example (dark)](/examples/dark/form.png)

