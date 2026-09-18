---
title: Section
description: Section groups related fields under a heading with optional description, icon, aside layout, and collapsible body.
---

## Introduction

Section groups related fields under a heading with optional description, icon, aside layout, and collapsible body. Compact mode tightens vertical rhythm for dense admin forms.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic section

Heading plus nested schema.

```python
Section.make('profile')
    .heading('Profile')
    .schema([TextInput.make('name').label('Name')])
```

![Orbit Basic section (light)](/examples/light/schemas/section/basic.png)

![Orbit Basic section (dark)](/examples/dark/schemas/section/basic.png)

## Collapsible section

Advanced blocks collapsed by default.

```python
Section.make('advanced')
    .heading('Advanced')
    .collapsible()
    .collapsed()
    .schema([Toggle.make('debug')])
```

![Orbit Collapsible section (light)](/examples/light/schemas/section/collapsible.png)

![Orbit Collapsible section (dark)](/examples/dark/schemas/section/collapsible.png)

## Compact section

Tighter spacing with optional icon.

```python
Section.make('profile')
    .heading('Profile')
    .compact()
    .icon('heroicon-o-user')
    .schema([...])
```

![Orbit Compact section (light)](/examples/light/schemas/section/compact.png)

![Orbit Compact section (dark)](/examples/dark/schemas/section/compact.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
