---
title: Toggle
description: Toggle is a styled switch built on Checkbox semantics — same wire:model binding, different visual treatment.
---

## Introduction

Toggle is a styled switch built on Checkbox semantics — same wire:model binding, different visual treatment. Pair toggles in Flex rows for compact settings panels.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic toggle

![Orbit Basic toggle (light)](/examples/light/forms/toggle/basic.png)

![Orbit Basic toggle (dark)](/examples/dark/forms/toggle/basic.png)

On/off switch with label.

```python
Toggle.make('active').label('Active account')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
