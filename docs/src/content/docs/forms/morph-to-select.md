---
title: Morph-to select
description: MorphToSelect pairs a type picker with a searchable id select — assign polymorphic relations (User vs Team) from one field.
---

## Introduction

MorphToSelect pairs a type picker with a searchable id select — assign polymorphic relations (User vs Team) from one field.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic morph-to select

![Orbit Basic morph-to select (light)](/examples/light/forms/morph-to-select/basic.png)

![Orbit Basic morph-to select (dark)](/examples/dark/forms/morph-to-select/basic.png)

User or team assignee.

```python
MorphToSelect.make('assignee')
    .label('Assignee')
    .searchable()
    .types([{'type': 'user', 'label': 'User', 'options': {'1': 'Ada'}}])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
