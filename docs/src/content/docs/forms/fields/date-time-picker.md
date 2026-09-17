---
title: DateTimePicker
description: Orbit DateTimePicker using native datetime-local input.
---

Date plus time — launches, deadlines, and “don’t forget the timezone later.”

## Standalone

```python
from almasix.orbit.forms import Form, DateTimePicker

form = Form.make("demo").schema([
        DateTimePicker.make("published_at")
            .label("Published at")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, DateTimePicker

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            DateTimePicker.make("scheduled_at").required(),
            DateTimePicker.make("archived_at").disabled(True),
        ])
```

## Key methods

- `Sets `input_type` to `datetime-local``
- `.required() / .default(...)`
- `.disabled(...) / .visible(...) / .readonly()`
- `.live() for live wire sync`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/form.png)

![Orbit form example (dark)](/examples/dark/form.png)

