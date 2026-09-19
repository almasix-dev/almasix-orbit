---
title: Custom fields
description: Build custom Orbit form fields by subclassing Field or composing ViewField.
---

## Introduction

Most admin UIs never need a custom field — compose TextInput, Select, Repeater, and schema layouts first. When you do, pick one of two paths:

1. **`ViewField`** — read-only HTML/callable content inside the schema (no input wiring).
2. **Subclass `Field`** — override `render()` for interactive controls that participate in state, validation, and dehydrate.

Custom fields still honor visibility, disabled state, rules, and content slots when you go through the base APIs. Scaffold with `smith make:orbit-field Rating` → `app/orbit/shared/fields/rating.py` (shared across panels; import where needed — never auto-discovered).

## Prefer ViewField for HTML-only

When you only need a labeled summary, badge, or chart embed, use `ViewField` instead of a subclass. Defaults to `_dehydrated = False`.

```python title="app/orbit/resources/invoice_resource.py"
from almasix.orbit.forms import ViewField

ViewField.make('aging')
    .label('Aging')
    .content(lambda record=None, **_: render_aging_partial(record))
```

![Orbit Prefer ViewField for HTML-only (light)](/examples/light/forms/view-field/basic.png)

![Orbit Prefer ViewField for HTML-only (dark)](/examples/dark/forms/view-field/basic.png)

## Subclass Field

Override `render(self, state=None, **ctx)` and usually:

- Return `""` when `not self.is_visible(**ctx)`.
- Resolve `name = self.get_state_path() or ""`.
- Build control HTML with `self._wire_binding(name)`, `self._common_input_attrs(**ctx)`, and disabled/readonly checks.
- Wrap with `self.wrap_field(name, control, **ctx)` so labels, hints, errors, affixes, and content slots keep working.

```python title="app/orbit/shared/fields/rating.py"
from typing import Any
from almasix.orbit.forms import Field
from almasix.orbit.support.html import e

class Rating(Field):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self._max = 5

    def max_stars(self, count: int) -> "Rating":
        self._max = count
        return self

    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        val = 1 if state is None else int(state)
        disabled = " disabled" if self.is_disabled(**ctx) or self.is_readonly() else ""
        control = (
            f'<input class="or-input or-rating" id="or-{name}" type="range" '
            f'min="1" max="{self._max}" name="{name}" value="{val}"{disabled}'
            f'{self._wire_binding(name)} />'
        )
        return self.wrap_field(name, control, **ctx)
```

![Orbit Subclass Field (light)](/examples/light/forms/slider/basic.png)

![Orbit Subclass Field (dark)](/examples/dark/forms/slider/basic.png)

## Using the custom field

Instantiate with `.make()` and chain inherited fluent helpers — rules, slots, `disabled_on`, trim, etc. all work because they live on `Field` / `Component`.

```python title="app/orbit/resources/review_resource.py"
from app.orbit.shared.fields.rating import Rating

Rating.make('score')
    .label('Score')
    .max_stars(5)
    .required()
    .helper_text('1 = poor, 5 = excellent')
    .above_content('Customer rating')
```

![Orbit Using the custom field (light)](/examples/light/forms/slider/range.png)

![Orbit Using the custom field (dark)](/examples/dark/forms/slider/range.png)

## Subclass ViewField

For structured read-only widgets that still want ViewField’s defaults (non-dehydrated, labeled body), subclass `ViewField` and override `content` or `render`.

```python title="app/orbit/shared/fields/status_badge.py"
from typing import Any
from almasix.orbit.forms import ViewField
from almasix.orbit.support.evaluate import evaluate
from almasix.orbit.support.html import e

class StatusBadge(ViewField):
    def render(self, state: Any = None, **ctx: Any) -> str:
        if not self.is_visible(**ctx):
            return ""
        name = e(self.get_state_path() or "")
        label = e(self.get_label(**ctx))
        raw = evaluate(self._view_html, state=state, **ctx) if self._view_html else state
        body = f'<span class="or-badge">{e(raw or "")}</span>'
        return (
            f'<div class="or-field or-field-ViewField or-field-StatusBadge" data-field="{name}">'
            f'<span class="or-label">{label}</span>'
            f'<div class="or-view-field">{body}</div></div>'
        )
```

![Orbit Subclass ViewField (light)](/examples/light/forms/view-field/callable.png)

![Orbit Subclass ViewField (dark)](/examples/dark/forms/view-field/callable.png)

## Validation on custom fields

Call `.rules()` / `.required()` / helpers in the resource, or append defaults in `__init__`. `Form.validate` only sees fields returned by `iter_fields` with a state path — ensure `make('score')` sets the name.

```python title="app/orbit/resources/review_resource.py"
Rating.make('score')
    .required()
    .rules(lambda value, **_: True if value and int(value) >= 1 else 'Pick a rating.')
```

![Orbit Validation on custom fields (light)](/examples/light/forms/text-input/required.png)

![Orbit Validation on custom fields (dark)](/examples/dark/forms/text-input/required.png)

## Dehydrate and trim

If your control stores strings, `.trim()`, `.strip_characters()`, and `.dehydrate_state_using()` apply through `apply_dehydrate_transforms` when the host dehydrates Field instances. Opt out of dehydration with `.dehydrated(False)` for display-only subclasses.

```python title="app/orbit/shared/fields/rating.py"
Rating.make('score')
    .dehydrate_state_using(lambda value, **_: int(value or 0))
```

![Orbit Dehydrate and trim (light)](/examples/light/forms/money-input/usd.png)

![Orbit Dehydrate and trim (dark)](/examples/dark/forms/money-input/usd.png)

## Packaging and discovery

Put shared fields under `app/orbit/shared/fields/` and import them in resources. Do **not** expect auto-discovery — register by import only. Keep SDUI in mind: `to_dict()` on Component dumps configuration for hosts that serialize schemas.

```python title="terminal"
smith make:orbit-field Rating
# → app/orbit/shared/fields/rating.py
```

```python title="app/orbit/resources/review_resource.py"
from app.orbit.shared.fields.rating import Rating

# Import explicitly — fields are never auto-discovered.
Rating.make('score').label('Score').required()
```

![Orbit Packaging and discovery (light)](/examples/light/forms/slider/basic.png)

![Orbit Packaging and discovery (dark)](/examples/dark/forms/slider/basic.png)

## When not to subclass

Reach for a custom `Field` only when existing components cannot express the control. Composition is cheaper to maintain and keeps Filament-parity helpers for free.

```python title="app/orbit/resources/product_resource.py"
# Extra chrome around TextInput — content slots, not a subclass:
TextInput.make('sku').above_label('<span class="or-badge">Inventory</span>')

# Read-only HTML — ViewField / Placeholder:
ViewField.make('hint').content('Prices exclude tax.')

# Money / OTP — packaged fields:
MoneyInput.make('price').currency('USD')
OneTimeCodeInput.make('otp').length(6)
```

![Orbit When not to subclass (light)](/examples/light/forms/money-input/usd.png)

![Orbit When not to subclass (dark)](/examples/dark/forms/money-input/usd.png)

| Need | Prefer |
|------|--------|
| Extra HTML around an existing input | Content slots / Section |
| Read-only HTML | `ViewField` / `Placeholder` |
| Repeated rows | `Repeater` / `Builder` |
| Currency | `MoneyInput` |
| OTP autocomplete | `OneTimeCodeInput` |

See [Validation](/forms/validation/) for rule helpers and [Closures](/forms/closures/) for injectable utilities inside custom `render()` / content callables.
