---
title: Toggle buttons
description: ToggleButtons render segmented radio controls styled as button groups — great for visibility, alignment, or enum-like choices with few options.
---

## Introduction

ToggleButtons render segmented radio controls styled as button groups — great for visibility, alignment, or enum-like choices with few options.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic toggle buttons

Public / private / draft visibility.

```python
ToggleButtons.make('visibility')
    .label('Visibility')
    .options({'public': 'Public', 'private': 'Private'})
```

![Orbit Basic toggle buttons (light)](/examples/light/forms/toggle-buttons/basic.png)

![Orbit Basic toggle buttons (dark)](/examples/dark/forms/toggle-buttons/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
