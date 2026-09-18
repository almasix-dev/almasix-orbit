---
title: Placeholder
description: Placeholder renders static prose inside the schema — useful for section intros, upgrade prompts, or spacing without a bound field.
---

## Introduction

Placeholder renders static prose inside the schema — useful for section intros, upgrade prompts, or spacing without a bound field.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic placeholder

![Orbit Basic placeholder (light)](/examples/light/forms/placeholder/basic.png)

![Orbit Basic placeholder (dark)](/examples/dark/forms/placeholder/basic.png)

Non-input informational slot.

```python
Placeholder.make('note')
    .content('This slot is reserved for future fields.')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
