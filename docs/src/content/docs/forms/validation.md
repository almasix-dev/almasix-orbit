---
title: Validation
description: Validate Orbit form fields with rule strings and callables.
---

Forms validate with `form.validate(data)`, which walks nested layouts and applies string rules and callables.

```python
from almasix.orbit.forms import Form, TextInput

form = Form.make().schema([
    TextInput.make("email").required().email().unique("users", "email"),
    TextInput.make("password").required().confirmed(),
    TextInput.make("password_confirmation").required(),
])

errors = form.validate({"email": "a", "password": "x", "password_confirmation": "y"})
```

Register database hooks with `Form.unique_using(...)` / `Form.exists_using(...)`.

See the [Forms overview](/forms/overview/) for the full rule catalog. Field helpers: `.unique()`, `.exists()`, `.regex()`, `.between()`, `.validation_attribute()`, `.validation_messages({…})`.

## Preview

![Orbit forms/overview (light)](/examples/light/forms/overview.png)

![Orbit forms/overview (dark)](/examples/dark/forms/overview.png)
