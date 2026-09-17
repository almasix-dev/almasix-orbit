---
title: CheckboxList
description: Orbit CheckboxList — multi-select rendered as a vertical checkbox group.
---

Many options, many checks — permissions, tags, “pick your toppings.”

## Standalone

```python
from almasix.orbit.forms import Form, CheckboxList

form = Form.make("demo").schema([
        CheckboxList.make("permissions")
            .options({
                "read": "Read",
                "write": "Write",
                "delete": "Delete",
            })
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, CheckboxList

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            CheckboxList.make("channels")
                .options({"email": "Email", "sms": "SMS", "push": "Push"})
                .required(),
        ])
```

## Key methods

- `.options(dict | callable) — multiple is always on`
- `.label(...) / .helper_text(...)`
- `.disabled(...) / .visible(...) / .required(...)`
- `.default([...]) for pre-checked values`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/form.png)

![Orbit form example (dark)](/examples/dark/form.png)

