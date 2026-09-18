---
title: Table select
description: TableSelect presents options with table-like chrome while still dehydrating a single (or multiple) key.
---

## Introduction

TableSelect presents options with table-like chrome while still dehydrating a single (or multiple) key. Prefer it when labels need columns of context beyond a flat Select list.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Table select

![Orbit Table select (light)](/examples/light/forms/select/basic.png)

![Orbit Table select (dark)](/examples/dark/forms/select/basic.png)

Renders like a select with table-oriented class hooks.

```python
TableSelect.make('post_id').label('Post').options({'1': 'Launch', '2': 'Hosts'})
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
