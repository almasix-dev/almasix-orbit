---
title: Custom fields
description: Build custom Orbit form fields by subclassing Field or composing ViewField.
---

## Introduction

Most admin UIs never need a custom field — combine TextInput, Select, and layouts first. When you do, subclass `Field` and override `render()`, or drop arbitrary HTML into a `ViewField`. Custom fields still participate in `validate()` / `dehydrate()` when they expose a state path and rules.

```python
from almasix.orbit.forms import Field

class Rating(Field):
    def render(self, state=None, **ctx):
        name = self.get_state_path() or ""
        return self.wrap_field(
            name,
            f'<input class="or-input" type="range" min="1" max="5" '
            f'name="{name}" value="{state or 1}" {self._wire_binding(name)} />',
            **ctx,
        )
```

![Orbit money input (light)](/examples/light/forms/money-input/usd.png)

![Orbit money input (dark)](/examples/dark/forms/money-input/usd.png)

Prefer composing existing fields inside a `ViewField` or schema layout when you only need custom markup. See the orbit-admin `MoneyInput` demo and [Money input](/forms/money-input/) for a packaged currency field.

Scaffold with `smith make:orbit-field Rating` → `app/orbit/shared/fields/rating.py` (shared across panels; import where needed — never auto-discovered).
