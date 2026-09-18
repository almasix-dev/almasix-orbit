---
title: Flex
description: Flex arranges children in a responsive row that stacks below a breakpoint.
---

## Introduction

Flex arranges children in a responsive row that stacks below a breakpoint. Use from_breakpoint('md') for side-by-side fields on desktop.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic flex

Responsive two-up layout.

```python
Flex.make()
    .from_breakpoint('md')
    .schema([TextInput.make('left'), TextInput.make('right')])
```

![Orbit Basic flex (light)](/examples/light/schemas/flex/basic.png)

![Orbit Basic flex (dark)](/examples/dark/schemas/flex/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
