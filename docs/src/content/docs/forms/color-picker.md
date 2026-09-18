---
title: Color picker
description: ColorPicker wraps the native color input for brand swatches and theme tokens.
---

## Introduction

ColorPicker wraps the native color input for brand swatches and theme tokens. Values dehydrate as hex strings.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic color picker

Single color selection.

```python
ColorPicker.make('brand')
    .label('Brand color')
```

![Orbit Basic color picker (light)](/examples/light/forms/color-picker/basic.png)

![Orbit Basic color picker (dark)](/examples/dark/forms/color-picker/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
