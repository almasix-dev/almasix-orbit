---
title: Tabs
description: Tabs split a form into horizontal panels — each tab owns its own schema.
---

## Introduction

Tabs split a form into horizontal panels — each tab owns its own schema. Icons and badges help surface counts or status without leaving the page.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic tabs

![Orbit Basic tabs (light)](/examples/light/schemas/tabs/basic.png)

![Orbit Basic tabs (dark)](/examples/dark/schemas/tabs/basic.png)

General and SEO panels.

```python
(
    Tabs.make('main')
    .tabs({'label': 'General', 'schema': [...]}, {'label': 'SEO', 'schema': [...]})
    .active_tab(0)
)
```

## Tabs with badges

![Orbit Tabs with badges (light)](/examples/light/schemas/tabs/with-badges.png)

![Orbit Tabs with badges (dark)](/examples/dark/schemas/tabs/with-badges.png)

Icons and numeric badges on tab labels.

```python
(
    Tabs.make('main')
    .tabs({'label': 'SEO', 'icon': 'heroicon-o-magnifying-glass', 'badge': '3', 'schema': [...]})
)
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
