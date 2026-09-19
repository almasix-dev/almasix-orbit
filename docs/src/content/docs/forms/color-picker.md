---
title: Color picker
description: ColorPicker is a native color input for hex brand and theme values.
---

## Introduction

`ColorPicker` sets `type="color"` on the shared Field input render path. Browsers show a native color well; dehydrated values are typically `#rrggbb`. Pair with `.hex_color()` validation when you also accept typed hex in other fields, or keep ColorPicker for the constrained UI.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic color picker

Labeled color well for brand colors, status accents, and theme tokens.

```python title="app/orbit/resources/example_resource.py"
ColorPicker.make('brand_color')
    .label('Brand color')
    .default('#0ea5e9')
```

![Orbit Basic color picker (light)](/examples/light/forms/color-picker/basic.png)

![Orbit Basic color picker (dark)](/examples/dark/forms/color-picker/basic.png)

## Required brand color

Shared Field helpers apply — require a selection and optionally disable on view operations.

```python title="app/orbit/resources/example_resource.py"
ColorPicker.make('accent')
    .label('Accent')
    .required()
    .disabled_on('view')
```

![Orbit Required brand color (light)](/examples/light/forms/color-picker/required.png)

![Orbit Required brand color (dark)](/examples/dark/forms/color-picker/required.png)

## With helper and hint

Document contrast or usage with helper/hint chrome around the native control.

```python title="app/orbit/resources/example_resource.py"
ColorPicker.make('sidebar')
    .label('Sidebar')
    .hint('Used in the customer portal')
    .helper_text('Prefer WCAG AA contrast against white.')
```

![Orbit With helper and hint (light)](/examples/light/forms/color-picker/with-hint.png)

![Orbit With helper and hint (dark)](/examples/dark/forms/color-picker/with-hint.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
