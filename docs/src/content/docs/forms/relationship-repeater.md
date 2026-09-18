---
title: Relationship repeater
description: RelationshipRepeater is a Repeater tuned for related models — same item chrome (add, remove, clone, reorder) with relationship metadata for hydrate/mutate ho…
---

## Introduction

RelationshipRepeater is a Repeater tuned for related models — same item chrome (add, remove, clone, reorder) with relationship metadata for hydrate/mutate hooks. Use it when nested rows map to hasMany / belongsToMany records rather than free-form JSON.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic repeater

![Orbit Basic repeater (light)](/examples/light/forms/repeater/basic.png)

![Orbit Basic repeater (dark)](/examples/dark/forms/repeater/basic.png)

Simple stacked items with add/remove.

```python
Repeater.make('items').label('Line items').schema([TextInput.make('name').label('Name')]).default_items(1)
```

## Cloneable and reorderable

![Orbit Cloneable and reorderable (light)](/examples/light/forms/repeater/cloneable-reorderable.png)

![Orbit Cloneable and reorderable (dark)](/examples/dark/forms/repeater/cloneable-reorderable.png)

Duplicate rows and move up/down.

```python
Repeater.make('items').cloneable().reorderable().collapsible().schema([...])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
