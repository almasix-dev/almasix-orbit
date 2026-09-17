---
title: Time picker
description: Orbit TimePicker using native time input.
---

Just the clock — opening hours, reminder times, quiet hours.

## Standalone

```python
from almasix.orbit.forms import Form, TimePicker

form = Form.make("demo").schema([
        TimePicker.make("opens_at").label("Opens at").default("09:00")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, TimePicker

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            TimePicker.make("reminder_at").required(),
            TimePicker.make("quiet_until"),
        ])
```

## Key methods

- `Sets `input_type` to `time``
- `.default("09:00") / .required()`
- `.disabled(...) / .visible(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/forms/overview.png)

![Orbit form example (dark)](/examples/dark/forms/overview.png)

