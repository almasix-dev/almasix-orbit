---
title: Color picker
description: ColorPicker shows a swatch, editable hex value, and optional copy button.
---

## Introduction

`ColorPicker` renders a compact control: a native color swatch beside a hex text field (and a Copy button by default). Both inputs stay in sync via Alpine; the text field is what the form submits (`#rrggbb`).

Pair with `.hex_color()` when you also accept typed hex elsewhere, or rely on ColorPicker for the constrained UI.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic color picker

Swatch + hex for brand colors, status accents, and theme tokens.

```python title="app/orbit/resources/example_resource.py"
ColorPicker.make('brand_color')
    .label('Brand color')
    .default('#0ea5e9')
```

![Orbit Basic color picker (light)](/examples/light/forms/color-picker/basic.png)

![Orbit Basic color picker (dark)](/examples/dark/forms/color-picker/basic.png)

## Without copy

`.copyable(False)` hides the clipboard button when you only need selection.

```python title="app/orbit/resources/example_resource.py"
ColorPicker.make('accent').copyable(False)
```

## Required brand color

Shared Field helpers apply — require a selection and optionally disable on view operations.

```python title="app/orbit/resources/example_resource.py"
ColorPicker.make('brand_color')
    .label('Brand color')
    .required()
    .disabled(lambda: False)
```

![Orbit Required color picker (light)](/examples/light/forms/color-picker/required.png)

![Orbit Required color picker (dark)](/examples/dark/forms/color-picker/required.png)

## API cheat sheet

| Method | Role |
|--------|------|
| `.copyable()` | Show Copy (default `True`) |
| Shared Field helpers | `.label()`, `.required()`, `.default()`, `.disabled()`, … |
