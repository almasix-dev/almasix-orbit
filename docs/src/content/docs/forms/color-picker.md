---
title: Color picker
description: ColorPicker wraps the native color input for brand swatches and theme tokens.
---

## Introduction

ColorPicker wraps the native color input for brand swatches and theme tokens. Values dehydrate as hex strings.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic color picker

![Orbit Basic color picker (light)](/examples/light/forms/color-picker/basic.png)

![Orbit Basic color picker (dark)](/examples/dark/forms/color-picker/basic.png)

Single color selection.

```python
ColorPicker.make('brand')
    .label('Brand color')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
