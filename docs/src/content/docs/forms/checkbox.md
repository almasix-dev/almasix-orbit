---
title: Checkbox
description: Orbit Checkbox field for boolean form state.
---

A boolean with a label beside it — featured, active, “yes I agree,” etc.

## Standalone

```python
from almasix.orbit.forms import Form, Checkbox

form = Form.make("demo").schema([
        Checkbox.make("featured").label("Featured on homepage")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Checkbox

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Checkbox.make("is_published").label("Published"),
            Checkbox.make("notify").default(True),
        ])
```

## Key methods

- `.label(...) — rendered next to the input`
- `.default(True|False)`
- `.disabled(...) / .visible(...) / .readonly()`
- `.required(...) when the box must be checked`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).


## Preview

![Orbit forms/checkbox-toggle (light)](/examples/light/forms/checkbox-toggle.png)

![Orbit forms/checkbox-toggle (dark)](/examples/dark/forms/checkbox-toggle.png)
