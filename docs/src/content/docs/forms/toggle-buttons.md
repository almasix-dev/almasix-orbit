---
title: Toggle buttons
description: ToggleButtons render segmented radio controls styled as button groups — great for visibility, alignment, or enum-like choices with few options.
---

## Introduction

ToggleButtons render segmented radio controls styled as button groups — great for visibility, alignment, or enum-like choices with few options.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic toggle buttons

![Orbit Basic toggle buttons (light)](/examples/light/forms/toggle-buttons/basic.png)

![Orbit Basic toggle buttons (dark)](/examples/dark/forms/toggle-buttons/basic.png)

Public / private / draft visibility.

```python
ToggleButtons.make('visibility').label('Visibility').options({'public': 'Public', 'private': 'Private'})
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
