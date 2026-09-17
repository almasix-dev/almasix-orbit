---
title: One-time code input
description: Orbit OneTimeCodeInput for verification codes and OTP fields.
---

OTP-friendly text input with `autocomplete="one-time-code"`.

## Standalone

```python
from almasix.orbit.forms import Form, OneTimeCodeInput

form = Form.make("demo").schema([
        OneTimeCodeInput.make("code")
            .label("Verification code")
            .required()
            .max_length(6)
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, OneTimeCodeInput

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            OneTimeCodeInput.make("otp").required().max_length(6),
            OneTimeCodeInput.make("backup_code").helper_text("From your recovery list"),
        ])
```

## Key methods

- `Inherits TextInput; autocomplete defaults to `one-time-code``
- `.max_length(n) / .required()`
- `.autocomplete(...) to override`
- `.disabled(...) / .visible(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/forms/overview.png)

![Orbit form example (dark)](/examples/dark/forms/overview.png)

