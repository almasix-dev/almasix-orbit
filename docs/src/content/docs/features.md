---
title: Features
description: What’s in the Orbit box — a practical checklist.
---

A straight inventory of what ships today. For narrative guides, start at [Quick start](/getting-started/quick-start/).

## Panels & resources

- Panel brand, path, colors, font, middleware, login, auth guard
- Resource form / table / infolist hooks
- Default create / view / edit / delete (and bulk delete) actions
- Pages and relation managers
- Permission helpers (`view_any`, `view`, `create`, `update`, `delete`)
- Navigation items with groups, icons, and sort
- `render_shell` HTML chrome with vendor assets
- `PanelRegistry` singleton via `OrbitServiceProvider`
- `LiveResource` test helper

## Forms & schemas

- Text, textarea, select, checkbox, toggle, radio, hidden, placeholder
- Date / time / datetime pickers, file upload, color, slider
- Rich / markdown / code editors (textarea-based)
- Repeater, builder, relationship repeater
- Multi-select, toggle buttons, one-time code
- String validation rules (`required`, `email`, `numeric`, `integer`, `url`, `min`/`max`)
- Grid, section, tabs, fieldset, wizard layouts
- State fill / dehydrate / render

## Tables

- Searchable / sortable / toggleable columns
- Badge, boolean, image, color, tags columns
- Filters (select, ternary, groups) with `.apply`
- Row, bulk, and header action slots
- Pagination, striped rows, empty states
- In-memory records with search + sort

## Actions

- Custom actions with authorize, confirm, modal form, URL, notifications
- Create / edit / view / delete / delete-bulk presets

## Infolists

- Text, icon, image, color, code, key-value, repeatable entries
- Badge, copyable, prose, markdown helpers

## Notifications & widgets

- Success / danger / warning / info notifications
- Flash, database, and broadcast channels
- Stats overview, chart, and table widgets

## Query builder & support

- Text / select / boolean / date / number constraints
- Operators: equals, contains, comparisons, set checks, `in`
- Fluent `Component` base, colors, Heroicons, `e` / `tag` helpers

## Rendering stack

- Conduit + Alpine for interactive bits
- Semantic `.or-*` CSS (Outfit + Almasix orange by default)
- `@orbitStyles` / `@orbitScripts` Prism directives
- Publishable `orbit-assets` tag

:::note[Still cooking]
`discover_*` path hooks and `smith make:orbit-resource` are API-shaped — register classes explicitly and scaffold by hand (or copy the quick start) until generators land.
:::
