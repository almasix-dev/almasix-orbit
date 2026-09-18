---
title: Toggle buttons
description: Orbit ToggleButtons — select options rendered as segmented buttons.
---

Radio options that look like a button strip — status, size, mood.

## Standalone

```python
from almasix.orbit.forms import Form, ToggleButtons

form = Form.make("demo").schema([
        ToggleButtons.make("size")
            .options({"sm": "Small", "md": "Medium", "lg": "Large"})
            .default("md")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, ToggleButtons

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            ToggleButtons.make("status")
                .options({"draft": "Draft", "live": "Live"})
                .required(),
        ])
```

## Key methods

- `.options(dict | callable)`
- `.default(...) / .required(...)`
- `.disabled(...) / .visible(...) / .label(...)`
- `Active option gets `is-active` on the label`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).


## Preview

![Orbit forms/toggle-buttons (light)](/examples/light/forms/toggle-buttons.png)

![Orbit forms/toggle-buttons (dark)](/examples/dark/forms/toggle-buttons.png)
