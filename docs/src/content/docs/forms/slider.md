---
title: Slider
description: Slider wraps a range input with optional pip marks for volume, priority, or percentage selection.
---

## Introduction

Slider wraps a range input with optional pip marks for volume, priority, or percentage selection.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic slider

![Orbit Basic slider (light)](/examples/light/forms/slider/basic.png)

![Orbit Basic slider (dark)](/examples/dark/forms/slider/basic.png)

0–100 range control.

```python
Slider.make('volume').label('Volume').min_value(0).max_value(100)
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
