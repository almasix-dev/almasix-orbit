---
title: Placeholder
description: Placeholder renders static prose inside the schema — useful for section intros, upgrade prompts, or spacing without a bound field.
---

## Introduction

Placeholder renders static prose inside the schema — useful for section intros, upgrade prompts, or spacing without a bound field.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic placeholder

Non-input informational slot.

```python
Placeholder.make('note')
    .content('This slot is reserved for future fields.')
```

![Orbit Basic placeholder (light)](/examples/light/forms/placeholder/basic.png)

![Orbit Basic placeholder (dark)](/examples/dark/forms/placeholder/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
