---
title: Slider
description: Slider is a native range input with min, max, step, and optional pips metadata.
---

## Introduction

`Slider` sets `type="range"` and defaults to min `0`, max `100`, step `1`. It reuses Field’s input render path with an `or-slider` class. `.pips()` adds `data-pips="true"` for tick marks in panel CSS/JS. Values dehydrate as numbers/strings from the range control.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic slider

Default 0–100 volume-style control with Orbit label chrome.

```python title="app/orbit/resources/example_resource.py"
Slider.make('volume')
    .label('Volume')
    .default(50)
```

![Orbit Basic slider (light)](/examples/light/forms/slider/basic.png)

![Orbit Basic slider (dark)](/examples/dark/forms/slider/basic.png)

## Custom range and step

`.min_value()`, `.max_value()`, and `.step()` configure the native range attributes for fractional or narrow scales.

```python title="app/orbit/resources/example_resource.py"
Slider.make('rating')
    .label('Rating')
    .min_value(0)
    .max_value(5)
    .step(0.5)
    .default(3)
```

![Orbit Custom range and step (light)](/examples/light/forms/slider/range.png)

![Orbit Custom range and step (dark)](/examples/dark/forms/slider/range.png)

## Pips

`.pips()` marks the control for tick/pip rendering via `data-pips`. Visual ticks depend on panel styles.

```python title="app/orbit/resources/example_resource.py"
Slider.make('progress')
    .label('Progress')
    .min_value(0)
    .max_value(100)
    .step(10)
    .pips()
```

![Orbit Pips (light)](/examples/light/forms/slider/pips.png)

![Orbit Pips (dark)](/examples/dark/forms/slider/pips.png)

## Live slider

`.live()` binds with live wire semantics so dependent fields update while dragging (host permitting).

```python title="app/orbit/resources/example_resource.py"
Slider.make('opacity')
    .label('Opacity')
    .min_value(0)
    .max_value(1)
    .step(0.05)
    .live()
```

![Orbit Live slider (light)](/examples/light/forms/slider/live.png)

![Orbit Live slider (dark)](/examples/dark/forms/slider/live.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
