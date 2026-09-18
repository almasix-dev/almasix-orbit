---
title: Hidden
description: Hidden fields dehydrate values without visible chrome — CSRF tokens, foreign keys, or serialized state.
---

## Introduction

Hidden fields dehydrate values without visible chrome — CSRF tokens, foreign keys, or serialized state. They render as plain hidden inputs and are omitted from screenshots.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Hidden field note

![Orbit Hidden field note (light)](/examples/light/forms/hidden/basic.png)

![Orbit Hidden field note (dark)](/examples/dark/forms/hidden/basic.png)

Not visually captured — renders as <input type="hidden">.

```python
Hidden.make('token')  # value set via fill() or default
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
