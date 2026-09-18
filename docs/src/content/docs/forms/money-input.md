---
title: Money input
description: MoneyInput extends TextInput with currency prefix symbols and data attributes for locale-aware formatting on the client.
---

## Introduction

MoneyInput extends TextInput with currency prefix symbols and data attributes for locale-aware formatting on the client. Choose currency codes for USD, EUR, GBP, or KES.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## USD

![Orbit USD (light)](/examples/light/forms/money-input/usd.png)

![Orbit USD (dark)](/examples/dark/forms/money-input/usd.png)

Dollar prefix and USD metadata.

```python
MoneyInput.make('price').label('Price').currency('USD')
```

## EUR

![Orbit EUR (light)](/examples/light/forms/money-input/eur.png)

![Orbit EUR (dark)](/examples/dark/forms/money-input/eur.png)

Euro prefix and EUR metadata.

```python
MoneyInput.make('price').label('Price').currency('EUR')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
