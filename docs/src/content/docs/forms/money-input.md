---
title: Money input
description: Currency amount field with prefix chrome (Filament MoneyInput-style).
---

`MoneyInput` is a numeric field with currency prefix, decimal step, and `data-currency` / `data-locale` attributes for client formatting hooks.

```python
from almasix.orbit.forms import Form, MoneyInput

form = Form.make().schema([
    MoneyInput.make("amount").currency("EUR").locale("de").label("Budget"),
])
```

## Key methods

- `.currency("USD"|"EUR"|"GBP"|"KES"|…)` — sets prefix symbol and `data-currency`
- `.locale("en")` — optional `data-locale`
- Inherits `TextInput` / `Field` chrome (prefix, suffix, actions, validation)

## Preview

![Orbit forms/color-money (light)](/examples/light/forms/color-money.png)

![Orbit forms/color-money (dark)](/examples/dark/forms/color-money.png)
