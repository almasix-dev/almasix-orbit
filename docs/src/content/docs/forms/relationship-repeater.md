---
title: Relationship repeater
description: RelationshipRepeater is a Repeater tuned for related models — same item chrome (add, remove, clone, reorder) with relationship metadata for hydrate/mutate ho…
---

## Introduction

RelationshipRepeater is a Repeater tuned for related models — same item chrome (add, remove, clone, reorder) with relationship metadata for hydrate/mutate hooks. Use it when nested rows map to hasMany / belongsToMany records rather than free-form JSON.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic repeater

Simple stacked items with add/remove.

```python
Repeater.make('items')
    .label('Line items')
    .schema([TextInput.make('name').label('Name')])
    .default_items(1)
```

![Orbit Basic repeater (light)](/examples/light/forms/repeater/basic.png)

![Orbit Basic repeater (dark)](/examples/dark/forms/repeater/basic.png)

## Cloneable and reorderable

Duplicate rows and move up/down.

```python
Repeater.make('items')
    .cloneable()
    .reorderable()
    .collapsible()
    .schema([...])
```

![Orbit Cloneable and reorderable (light)](/examples/light/forms/repeater/cloneable-reorderable.png)

![Orbit Cloneable and reorderable (dark)](/examples/dark/forms/repeater/cloneable-reorderable.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
