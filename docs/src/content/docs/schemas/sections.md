---
title: Section
description: Section groups related fields under a heading with optional description, icon, aside layout, and collapsible body.
---

## Introduction

Section groups related fields under a heading with optional description, icon, aside layout, and collapsible body. Compact mode tightens vertical rhythm for dense admin forms.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic section

![Orbit Basic section (light)](/examples/light/schemas/section/basic.png)

![Orbit Basic section (dark)](/examples/dark/schemas/section/basic.png)

Heading plus nested schema.

```python
Section.make('profile')
    .heading('Profile')
    .schema([TextInput.make('name').label('Name')])
```

## Collapsible section

![Orbit Collapsible section (light)](/examples/light/schemas/section/collapsible.png)

![Orbit Collapsible section (dark)](/examples/dark/schemas/section/collapsible.png)

Advanced blocks collapsed by default.

```python
Section.make('advanced')
    .heading('Advanced')
    .collapsible()
    .collapsed()
    .schema([Toggle.make('debug')])
```

## Compact section

![Orbit Compact section (light)](/examples/light/schemas/section/compact.png)

![Orbit Compact section (dark)](/examples/dark/schemas/section/compact.png)

Tighter spacing with optional icon.

```python
Section.make('profile')
    .heading('Profile')
    .compact()
    .icon('heroicon-o-user')
    .schema([...])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
