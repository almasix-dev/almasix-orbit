---
title: Checkbox
description: Checkbox renders a single boolean toggle with an inline label.
---

## Introduction

Checkbox renders a single boolean toggle with an inline label. Use CheckboxList when users pick many options from a set; use Toggle for on/off settings with switch styling.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic checkbox

Single boolean consent or feature flag.

```python
Checkbox.make('terms')
    .label('Accept terms and conditions')
```

![Orbit Basic checkbox (light)](/examples/light/forms/checkbox/basic.png)

![Orbit Basic checkbox (dark)](/examples/dark/forms/checkbox/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
