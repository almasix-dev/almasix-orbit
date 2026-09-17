---
title: Release notes
description: What’s new in Orbit — major and minor highlights.
---

Orbit follows Almasix’s major-line docs model. This page tracks notable
changes; pin a package version in production and read the matching line in the
header switcher.

## 0.x

First published line of Orbit — panels, resources, forms, tables, actions,
infolists, schemas, notifications, widgets, query builder, and the support
toolkit, rendered on Conduit + Alpine with semantic `.or-*` CSS.

Highlights:

- Fluent `Panel` / `Resource` / `Page` / `RelationManager` APIs
- Form fields with string validation rules
- Tables with search, sort, pagination, filters, and action slots
- Action presets for create / edit / view / delete (including bulk delete)
- Layout schemas: grid, section, tabs, fieldset, wizard
- Flash / database / broadcast notifications
- Stats, chart, and table widgets
- In-memory query builder with typed constraints
- `LiveResource` test helper
- Auto-discovered `OrbitServiceProvider` via `almasix.providers`

## Unreleased (`main`)

Working from the tip of `main`? Switch the docs to **main** in the header.
Breaking changes will land here before they become a new major.
