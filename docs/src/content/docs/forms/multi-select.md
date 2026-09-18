---
title: Multi select
description: MultiSelect extends Select for choosing many options at once.
---

## Introduction

MultiSelect extends Select for choosing many options at once. Options render as a multi native select (or searchable multi when combined with searchable). Use it for tags, roles, and any many-to-many style attribute that still fits a fixed option list.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Multi select

![Orbit Multi select (light)](/examples/light/forms/select/multiple.png)

![Orbit Multi select (dark)](/examples/dark/forms/select/multiple.png)

Multiple selection via MultiSelect.

```python
MultiSelect.make('tags').label('Tags').options({'orbit': 'Orbit', 'forms': 'Forms'})
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
