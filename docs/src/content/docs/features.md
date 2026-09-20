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

- Trigger styles: button, link, icon button, badge — plus size, outlined, icons, tooltip, keybindings
- URL actions with open-in-new-tab; authorize with tooltip / notification UX
- Full modal API: confirmation, form schema, slide-over, width, sticky chrome, labels, icons
- `ActionGroup` / `BulkActionGroup` dropdowns, button groups, and sections
- Create / edit / view / delete / replicate / force-delete / restore presets
- Import / export config bags with documented host-owned `Importer` / `Exporter` adapters

See [Actions overview](/actions/overview/).

## Infolists

- Text, icon, image, color, code, key-value, repeatable, and view entries
- Shared Entry chrome: labels, helpers, hints, placeholders, copyable, slots, affixes
- Text formatters: badges, icons, URLs, dates / since, money, numeric, markdown / HTML / prose, lists
- Image stacks, boolean icons, grammar-aware code blocks
- Empty `infolist()` falls back to a readonly form projection

See [Infolists overview](/infolists/overview/).

## Notifications

- Success / danger / warning / info notifications
- Flash, database, and broadcast channels

## Widgets & dashboard

- Stats overview with fluent `Stat` cards and Chart.js sparklines
- `ChartWidget` with Chart.js (default) or ApexCharts via `.chart_library`
- `TableWidget` for embedded dashboard tables
- Panel home [Dashboard](/panels/dashboard/) — columns, filters, multi-dashboard `route_path`

See [Widgets overview](/widgets/overview/).

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
Some Filament surfaces (SPA mode, relation managers depth, etc.) are still landing. Resource scaffolding with `--generate` is available — see [Resources](/resources/overview/).
:::
