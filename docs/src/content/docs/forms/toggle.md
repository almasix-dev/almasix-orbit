---
title: Toggle
description: Toggle is a styled switch built on Checkbox semantics — same wire:model binding, different visual treatment.
---

## Introduction

Toggle is a styled switch built on Checkbox semantics — same wire:model binding, different visual treatment. Pair toggles in Flex rows for compact settings panels.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic toggle

On/off switch with label.

```python
Toggle.make('active')
    .label('Active account')
```

![Orbit Basic toggle (light)](/examples/light/forms/toggle/basic.png)

![Orbit Basic toggle (dark)](/examples/dark/forms/toggle/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
