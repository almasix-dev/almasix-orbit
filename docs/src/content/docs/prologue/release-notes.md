---
title: Release notes
description: What’s new in Orbit — major and minor highlights.
---

Orbit follows Almasix’s major-line docs model. This page tracks notable
changes; pin a package version in production and read the matching line in the
header switcher.

## 0.x

Published Orbit line — panels, resources, forms, tables, actions, infolists,
schemas, notifications, widgets, query builder, and the support toolkit on
Conduit + Alpine with semantic `.or-*` CSS.

Highlights:

- Fluent `Panel` / `Resource` / `Page` / `RelationManager` APIs
- Standalone packages (forms, tables, …) render without a panel
- `evaluate()` + closures on labels, helpers, options, authorize, URLs, and more
- Real field and column renders (including repeaters, tags, editors, inline editors)
- Infolist falls back to a readonly form projection when unset
- View/Edit/Create default to **page URLs**; `.modal()` / confirmation for quick actions
- Navigation: groups, subgroups, custom items, layouts (`sidebar`, `top`, `sidebar_topbar`)
- Split sidebar → topbar secondary nav (Shamar-style)
- Query builder UI render over the constraint apply model
- `LiveResource` test helper
- Auto-discovered `OrbitServiceProvider` via `almasix.providers`

## 0.2.0

Filament-parity expansion across forms, schemas, tables, shell, and docs —
plus CRUD/selection fixes and a 99% coverage gate.

Highlights:

- Forms & schemas Filament parity (gallery screenshots, fluent docs snippets)
- Table UX: search, sort, filters, record URLs, column types, action menus
- Orbit shell: Conduit admin, branding, panel defaults, extendable auth pages
- Resource CRUD, selection/delete, and dropdown overflow fixes
- Docs: SEO, Filament-style previews, code-before-shots gallery polish
- Full coverage test suite with 99% fail-under CI gate

## Unreleased (`main`)

Working from the tip of `main`? Switch the docs to **main** in the header.
Breaking changes will land here before they become a new major.
