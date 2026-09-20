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

## Description

`.description(...)` is supporting copy under the heading — use it for “why this group exists” rather than field-level helpers.

```python
Section.make("billing")
    .heading("Billing")
    .description("Shown on invoices sent to the tenant owner.")
    .schema([TextInput.make("legal_name").required()])
```

![Orbit Section with description (light)](/examples/light/schemas/section/description.png)

![Orbit Section with description (dark)](/examples/dark/schemas/section/description.png)

## Aside

`.aside()` moves the heading into a side column so the fields sit beside the title on wide screens.

```python
Section.make("profile")
    .heading("Profile")
    .description("Public author details.")
    .aside()
    .schema([TextInput.make("name").required()])
```

![Orbit Aside section (light)](/examples/light/schemas/section/aside.png)

![Orbit Aside section (dark)](/examples/dark/schemas/section/aside.png)

`.secondary()` mutes the chrome. `.persist_collapsed()` keeps the open/closed state in the browser for collapsible sections.

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
