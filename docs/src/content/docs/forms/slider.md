---
title: Slider
description: Orbit Slider field using native range input.
---

A range input for scores, opacity, “how spicy is this incident?”

## Standalone

```python
from almasix.orbit.forms import Form, Slider

form = Form.make("demo").schema([
        Slider.make("priority").label("Priority").default(50)
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Slider

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Slider.make("opacity").helper_text("0–100"),
            Slider.make("volume").disabled(False),
        ])
```

## Key methods

- `Sets `input_type` to `range``
- `.default(n) / .rules("min:0", "max:100")`
- `.label(...) / .helper_text(...)`
- `.live() for continuous updates`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).


## Preview

![Orbit forms/overview (light)](/examples/light/forms/overview.png)

![Orbit forms/overview (dark)](/examples/dark/forms/overview.png)
