---
title: Fieldset
description: Fieldset wraps nested fields in semantic fieldset/legend chrome — accessibility-friendly grouping for addresses and payment blocks.
---

## Introduction

Fieldset wraps nested fields in semantic fieldset/legend chrome — accessibility-friendly grouping for addresses and payment blocks.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic fieldset

![Orbit Basic fieldset (light)](/examples/light/schemas/fieldset/basic.png)

![Orbit Basic fieldset (dark)](/examples/dark/schemas/fieldset/basic.png)

Billing address legend.

```python
Fieldset.make('billing')
    .label('Billing address')
    .schema([TextInput.make('line1'), TextInput.make('city')])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
