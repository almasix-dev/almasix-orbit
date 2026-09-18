---
title: Empty state
description: EmptyState renders centered heading and description when lists or repeaters have no items — reuse in tables and standalone schema slots.
---

## Introduction

EmptyState renders centered heading and description when lists or repeaters have no items — reuse in tables and standalone schema slots.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic empty state

![Orbit Basic empty state (light)](/examples/light/schemas/empty-state/basic.png)

![Orbit Basic empty state (dark)](/examples/dark/schemas/empty-state/basic.png)

No drafts placeholder.

```python
(
    EmptyState.make()
    .heading('No drafts')
    .description('Create one when you are ready.')
)
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
