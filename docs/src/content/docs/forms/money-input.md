---
title: Money input
description: MoneyInput extends TextInput with currency prefix symbols and data attributes for locale-aware formatting on the client.
---

## Introduction

MoneyInput extends TextInput with currency prefix symbols and data attributes for locale-aware formatting on the client. Choose currency codes for USD, EUR, GBP, or KES.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## USD

Dollar prefix and USD metadata.

```python
MoneyInput.make('price')
    .label('Price')
    .currency('USD')
```

![Orbit USD (light)](/examples/light/forms/money-input/usd.png)

![Orbit USD (dark)](/examples/dark/forms/money-input/usd.png)

## EUR

Euro prefix and EUR metadata.

```python
MoneyInput.make('price')
    .label('Price')
    .currency('EUR')
```

![Orbit EUR (light)](/examples/light/forms/money-input/eur.png)

![Orbit EUR (dark)](/examples/dark/forms/money-input/eur.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
