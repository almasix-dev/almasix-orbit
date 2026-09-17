---
title: Custom fields
description: Build custom Orbit form fields.
---

Subclass `Field` and override `render()`:

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

Prefer composing existing fields inside a `ViewField` or schema layout when you only need custom markup.

## Preview

![Orbit forms/color-money (light)](/examples/light/forms/color-money.png)

![Orbit forms/color-money (dark)](/examples/dark/forms/color-money.png)
