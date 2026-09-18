---
title: Empty state
description: EmptyState renders centered heading and description when lists or repeaters have no items — reuse in tables and standalone schema slots.
---

## Introduction

EmptyState renders centered heading and description when lists or repeaters have no items — reuse in tables and standalone schema slots.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic empty state

No drafts placeholder.

```python
EmptyState.make()
    .heading('No drafts')
    .description('Create one when you are ready.')
```

![Orbit Basic empty state (light)](/examples/light/schemas/empty-state/basic.png)

![Orbit Basic empty state (dark)](/examples/dark/schemas/empty-state/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
