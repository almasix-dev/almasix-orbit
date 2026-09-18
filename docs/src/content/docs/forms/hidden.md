---
title: Hidden
description: Hidden fields dehydrate values without visible chrome — CSRF tokens, foreign keys, or serialized state.
---

## Introduction

Hidden fields dehydrate values without visible chrome — CSRF tokens, foreign keys, or serialized state. They render as plain hidden inputs and are omitted from screenshots.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Hidden field note

Not visually captured — renders as <input type="hidden">.

```python
Hidden.make('token')  # value set via fill() or default
```

![Orbit Hidden field note (light)](/examples/light/forms/hidden/basic.png)

![Orbit Hidden field note (dark)](/examples/dark/forms/hidden/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
