---
title: Text input
description: Orbit TextInput field for single-line text, email, password, and friends.
---

Single-line text — the workhorse of every admin form.

## Standalone

```python
from almasix.orbit.forms import Form, TextInput

form = Form.make("demo").schema([
        TextInput.make("title")
            .label("Title")
            .placeholder("Shipping Orbit docs")
            .required()
            .max_length(200)
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            TextInput.make("title").required().max_length(200),
            TextInput.make("slug").helper_text("Used in URLs"),
            TextInput.make("email").email(),
        ])
```

## Key methods

- `.label(...) / .placeholder(...) / .helper_text(...)`
- `.required() / .rules(...)`
- `.email() / .password() / .numeric() / .integer() / .tel() / .url()`
- `.max_length(n) / .min_length(n)`
- `.default(...) / .live() / .readonly() / .disabled(...) / .visible(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/forms/text-input.png)

![Orbit form example (dark)](/examples/dark/forms/text-input.png)

