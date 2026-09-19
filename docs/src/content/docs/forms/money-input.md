---
title: Money input
description: MoneyInput extends TextInput with currency prefix symbols, decimal step, and data-currency metadata.
---

## Introduction

`MoneyInput` is a `TextInput` subclass that defaults to `type="number"`, `.step("0.01")`, `.input_mode("decimal")`, and a `$` prefix. `.currency(code)` swaps the prefix for known codes (`USD`, `EUR`, `GBP`, `KES`) or `"CODE "` for unknown codes, and sets `data-currency`. Optional `.locale()` adds `data-locale` for client formatting. The field class becomes `or-field-MoneyInput`.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## USD

Default currency chrome uses `$` and `USD` metadata — ideal for dollar amounts.

```python title="app/orbit/resources/example_resource.py"
MoneyInput.make('price')
    .label('Price')
    .currency('USD')
    .required()
```

![Orbit USD (light)](/examples/light/forms/money-input/usd.png)

![Orbit USD (dark)](/examples/dark/forms/money-input/usd.png)

## EUR

`.currency('EUR')` switches the prefix to `€` and updates `data-currency`.

```python title="app/orbit/resources/example_resource.py"
MoneyInput.make('price')
    .label('Price')
    .currency('EUR')
```

![Orbit EUR (light)](/examples/light/forms/money-input/eur.png)

![Orbit EUR (dark)](/examples/dark/forms/money-input/eur.png)

## Locale metadata

`.locale('en_US')` emits `data-locale` for host/client formatters without changing the numeric dehydrate value.

```python title="app/orbit/resources/example_resource.py"
MoneyInput.make('budget')
    .label('Budget')
    .currency('GBP')
    .locale('en_GB')
```

![Orbit Locale metadata (light)](/examples/light/forms/money-input/locale.png)

![Orbit Locale metadata (dark)](/examples/dark/forms/money-input/locale.png)

## Validation and bounds

Use `.min_value()` / `.max_value()` / `.between()` for amount ranges. Inherited TextInput helpers (prefix override, disabled, live) still apply after `.currency()`.

```python title="app/orbit/resources/example_resource.py"
MoneyInput.make('deposit')
    .label('Deposit')
    .currency('USD')
    .min_value(0)
    .max_value(10000)
    .step(0.01)
```

![Orbit Validation and bounds (light)](/examples/light/forms/money-input/bounds.png)

![Orbit Validation and bounds (dark)](/examples/dark/forms/money-input/bounds.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
