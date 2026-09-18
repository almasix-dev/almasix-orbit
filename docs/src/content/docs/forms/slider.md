---
title: Slider
description: Slider wraps a range input with optional pip marks for volume, priority, or percentage selection.
---

## Introduction

Slider wraps a range input with optional pip marks for volume, priority, or percentage selection.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic slider

0–100 range control.

```python
Slider.make('volume')
    .label('Volume')
    .min_value(0)
    .max_value(100)
```

![Orbit Basic slider (light)](/examples/light/forms/slider/basic.png)

![Orbit Basic slider (dark)](/examples/dark/forms/slider/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
