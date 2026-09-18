---
title: Validation
description: Validate Orbit form fields with rule strings, callables, and conditional required/prohibited rules.
---

## Introduction

Orbit validates with `form.validate(data)`, walking nested layouts (Section, Tabs, Wizard, Repeater schemas) and applying string rules plus callables. Errors return as `field → [messages]`. Database-backed `unique` / `exists` rules use checkers registered via `Form.unique_using(...)` and `Form.exists_using(...)`.

![Orbit form overview (light)](/examples/light/forms/overview.png)

![Orbit form overview (dark)](/examples/dark/forms/overview.png)

```python
from almasix.orbit.forms import Form, TextInput

form = Form.make().schema([
    TextInput.make("email").required().email().unique("users", "email"),
    TextInput.make("password").required().confirmed(),
    TextInput.make("password_confirmation").required(),
    TextInput.make("role").default("user"),
    TextInput.make("admin_code").required_if("role", "admin"),
    TextInput.make("guest_note").prohibited_if("role", "admin"),
])

errors = form.validate({
    "email": "a",
    "password": "x",
    "password_confirmation": "y",
    "role": "admin",
})
```

## Common rules

| Rule | Helper |
|------|--------|
| `required`, `nullable`, `filled` | `.required()` |
| `email`, `url`, `numeric`, `integer` | `.email()` / `.url()` / `.numeric()` |
| `confirmed`, `same:`, `different:` | `.confirmed()` via password patterns |
| `in:`, `not_in:`, `regex:` | `.rules(...)` / `.regex()` |
| `between:`, `min:`, `max:`, `gt:`… | `.between()` / `.min_value()` |
| `unique:`, `exists:` | `.unique()` / `.exists()` |
| `required_if:`, `required_unless:` | `.required_if()` / `.required_unless()` |
| `prohibited`, `prohibited_if:` | `.prohibited()` / `.prohibited_if()` |

Field helpers: `.validation_attribute()`, `.validation_messages({…})`.
