---
title: Fieldset
description: Fieldset wraps nested fields in semantic fieldset/legend chrome — accessibility-friendly grouping for addresses and payment blocks.
---

## Introduction

Fieldset wraps nested fields in semantic fieldset/legend chrome — accessibility-friendly grouping for addresses and payment blocks.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic fieldset

Billing address legend.

```python
Fieldset.make('billing')
    .label('Billing address')
    .schema([TextInput.make('line1'), TextInput.make('city')])
```

![Orbit Basic fieldset (light)](/examples/light/schemas/fieldset/basic.png)

![Orbit Basic fieldset (dark)](/examples/dark/schemas/fieldset/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
