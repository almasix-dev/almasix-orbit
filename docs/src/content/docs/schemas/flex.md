---
title: Flex
description: Flex arranges children in a responsive row that stacks below a breakpoint.
---

## Introduction

Flex arranges children in a responsive row that stacks below a breakpoint. Use from_breakpoint('md') for side-by-side fields on desktop.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic flex

![Orbit Basic flex (light)](/examples/light/schemas/flex/basic.png)

![Orbit Basic flex (dark)](/examples/dark/schemas/flex/basic.png)

Responsive two-up layout.

```python
Flex.make()
    .from_breakpoint('md')
    .schema([TextInput.make('left'), TextInput.make('right')])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
