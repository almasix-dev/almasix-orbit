---
title: Table select
description: TableSelect presents options with table-like chrome while still dehydrating a single (or multiple) key.
---

## Introduction

TableSelect presents options with table-like chrome while still dehydrating a single (or multiple) key. Prefer it when labels need columns of context beyond a flat Select list.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Table select

Renders like a select with table-oriented class hooks.

```python
TableSelect.make('post_id')
    .label('Post')
    .options({'1': 'Launch', '2': 'Hosts'})
```

![Orbit Table select (light)](/examples/light/forms/select/basic.png)

![Orbit Table select (dark)](/examples/dark/forms/select/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
