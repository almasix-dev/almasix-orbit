---
title: Release notes
description: What’s new in Orbit — major and minor highlights.
---

Orbit follows Almasix’s major-line docs model. This page tracks notable
changes; pin a package version in production and read the matching line in the
header switcher.

## Unreleased (`main`)

Working from the tip of `main`? Switch the docs to **main** in the header.
Changes land here before they become a tagged release.

## 0.4.3

Flowbite date/time pickers, notifications production adapter, demo showcase polish, and shell/form fixes after 0.4.2.

```bash title="terminal"
pip install -U 'almasix-orbit==0.4.3'
```

### Forms — date and time pickers

- `DatePicker`, `DateTimePicker`, and `TimePicker` default to Flowbite + Alpine (`orbitDatePicker`); use `.native(True)` for browser inputs
- New `WeekPicker`, `MonthPicker`, and `YearPicker`
- Time APIs: `.seconds()`, `.hours12()` / `.hours24()`, `.minute_step(n)`
- Temporal validation: `after_or_equal`, `before_or_equal`, `date_equals`, and datetime/time-aware `after` / `before`

### Notifications

- Panel bell can persist via Almasix’s polymorphic `notifications` table (`.database_notifications_using_almasix()`)
- `SqliteNotificationStore` retained for tests and non-ORM setups

### Demo

- Soft catalog reset (`demo:reset`) keeps cookie sessions; hourly schedule + HTTP/GHA reset for Render Free
- Larger Orbit Records seed and home/Insights widgets covering Chart.js and ApexCharts chart types
- Demo installs Almasix / Orbit / Conduit from **PyPI only** (no monorepo path installs)

### Fixes and UX

- TagsInput and CheckboxList array state persists on submit ([#97](https://github.com/almasix-dev/almasix-orbit/pull/97))
- Fresh-project shell UX polish ([#96](https://github.com/almasix-dev/almasix-orbit/pull/96))

## 0.4.2

Marketplace and plugin-scaffold polish after 0.4.1.

```bash title="terminal"
pip install -U 'almasix-orbit==0.4.2'
```

### Marketplace

- Listings live in [orbit-plugins](https://github.com/almasix-dev/orbit-plugins); docs sync the registry at build time
- Marketplace articles at [`/articles/`](/articles/)
- Listing pages embed GitHub `docs_url` READMEs beside the YAML overview
- Visit on GitHub and Star are separate actions; star counts match GitHub (no optimistic bumps)
- Sleeker plugin and author cards (icons, compact action pills)

### Plugins

- Official plugin [Orbit Permission](/plugins/orbit-permission/) (`almasix-orbit-permission`) — Users, Roles, and Permissions UI on `almasix-permission`
- `smith make:orbit-plugin` draft YAML now points authors at **orbit-plugins** instead of the Orbit docs tree

## 0.4.1

Patch: the default panel home (`GET /admin`) failed under Almasix’s controller binder because dashboard (and other) route actions used `**_e` / `**_extra`. Those catch-alls are gone; handlers take `request` plus optional `tenant` / `record_id` only.

```bash title="terminal"
pip install -U 'almasix-orbit==0.4.1'
```

## 0.4.0

Feature release after 0.3.1 — resources, forms, tables, actions, users, panels,
plugins, and the docs site.

**Breaking:** `app/orbit/{id}_panel.py` is no longer loaded. Move the registrar
to `app/orbit/{id}/panel.py` (the layout 0.3 already scaffolded). See
[Installation](/getting-started/installation/).

### Resources

- Relation managers on view/edit pages (ORM or in-memory rows)
- Panel global search (resource attributes → grouped results → topbar)
- Record titles in page headings and breadcrumbs
- Resource-level soft deletes (trashed filter, restore, force delete)

### Forms and schemas

- File upload via panel `/orbit-upload` (`UploadStorage`, memory default)
- Rich editor toolbar, merge tags, min-height
- MorphToSelect live search (`.options_using`)
- Modal table select and KeyValue host actions
- Searchable select combobox; remaining form/schema field depth

### Tables, actions, widgets, query builder

- Table overview: relationship columns, pagination modes, header chrome, poll, reorder
- Column types and filters
- In-process import/export (`ImmediateJobRunner`, CSV/JSON, `orbit-export-ready`)
- Widgets and dashboard
- Query builder AND/OR rules, typed widgets, `QueryBuilderFilter`

### Users, notifications, panels

- Multi-tenancy API and UX
- TOTP (`AppAuthentication`) and email MFA (`EmailAuthentication`) with `/mfa-challenge`
- SQLite notification store, broadcast hub, `/orbit-live`
- SPA navigation (`.spa()`), billing adapters, `PanelRegistry.get_by_path` / `get_by_domain`

### Plugins and support

- `smith make:orbit-plugin` / `python -m almasix.orbit plugin new` — package + listing YAML
- Community plugin catalog at [`/plugins/`](/plugins/) (docs-hosted YAML, catalog API)
- Support toolkit: `HtmlString`, palettes, icon aliases, `Component.key` / `.grow` / `.when`

### Docs

- Orbit-first learner pages, unique gallery shots
- Header Docs + Plugins menus; marketplace catalog layout
- Version trees: `/0.x/` from the latest `v0.*` tag, `/main/` from this commit

```bash title="terminal"
pip install -U 'almasix-orbit==0.4.0'
```

## 0.3.1

Patch release after [#44](https://github.com/almasix-dev/almasix-orbit/issues/44) / [#42](https://github.com/almasix-dev/almasix-orbit/issues/42) / [#39](https://github.com/almasix-dev/almasix-orbit/issues/39).

### Resource auto-generation from the database ([#44](https://github.com/almasix-dev/almasix-orbit/issues/44))

- `make:orbit-resource --generate` (Filament `--generate` parity) reflects the model's table via `Schema.columns` and stubs form fields + table columns with type intelligence (`Toggle` / `BooleanColumn`, `DateTimePicker`, `Textarea`, …)
- `--model=` links an ORM model (bare name or dotted path); when the model resolves without `--generate`, an interactive TTY asks whether to generate
- CI coverage gate raised to **100%**

### Scaffold & navigation polish ([#42](https://github.com/almasix-dev/almasix-orbit/issues/42))

- `make:orbit-resource` uses a plural navigation label (Artist → Artists) and no longer sets a default `Content` group
- `NavigationSubgroup` / `navigation_subgroup` (alias `navigation_sub_category` / `.sub_category()`): apps top-bar dropdowns, sidebar accordions, panel `.navigation_subgroup(s)()` registration with icon/sort/parent

### Interactive panel scaffolding ([#39](https://github.com/almasix-dev/almasix-orbit/issues/39))

- `make:orbit-resource|page|widget` prompt for a panel when several `app/orbit/{id}/panel.py` packages exist (skip with `--panel=…`; non-interactive defaults to `admin` or the first id)
- Missing class names are prompted on a TTY

```bash title="terminal"
pip install -U 'almasix-orbit==0.3.1'
```

## 0.3.0

Per-panel component directories ([#32](https://github.com/almasix-dev/almasix-orbit/issues/32) / [#33](https://github.com/almasix-dev/almasix-orbit/pull/33) / [#35](https://github.com/almasix-dev/almasix-orbit/pull/35) / [#36](https://github.com/almasix-dev/almasix-orbit/pull/36)).

**Breaking:** each panel owns its components under `app/orbit/{id}/` (flat `app/orbit/resources` is no longer the implied home).

Highlights:

- `orbit:install` / `make:orbit-panel` → `app/orbit/{id}/panel.py` + `resources/`, `pages/`, `widgets/`, `themes/` (stub `custom.css`)
- `make:orbit-resource|page|widget --panel=` writes into that panel’s tree
- `make:orbit-field` → `app/orbit/shared/fields/` (never auto-discovered)
- `.discover_panel_dirs()` discovers resources/pages/widgets **and** loads `themes/*.css`; FQCN dedupe; legacy `*_panel.py` still loads with `DeprecationWarning` (removed in 0.4)
- `.theme_package(...)` / `.theme_stylesheet(...)` for extra theme CSS
- Plugins **only** via `.plugin(...)` — no `{id}/plugins` autodisc
- Shared resources: explicit `.resources([...])` on each panel; `app/orbit/shared/` is never auto-pulled
- Login/register hosts bind form fields under `data.*` ([#35](https://github.com/almasix-dev/almasix-orbit/pull/35))

See [Installation](/getting-started/installation/) for the upgrade path from 0.2.x.

```bash title="terminal"
pip install -U 'almasix-orbit==0.3.0'
```

## 0.2.2

Scaffold wiring for panels under `app/orbit` ([#27](https://github.com/almasix-dev/almasix-orbit/issues/27) / [#28](https://github.com/almasix-dev/almasix-orbit/pull/28)) plus docs recovered after the 0.2.1 squash ([#29](https://github.com/almasix-dev/almasix-orbit/pull/29)).

Highlights:

- **`orbit:install`** writes `app/orbit/{id}_panel.py` and a thin `OrbitPanelProvider` that only calls `register_app_orbit_panels(...)`
- **`orbit:panel`** adds another `*_panel.py` (auto-discovered on next boot); provider stays thin
- Provider is listed in `config/app.py` automatically
- Docs: [Installation](/getting-started/installation/) (layout + discovery), [Quick start](/getting-started/quick-start/), [Panel configuration](/panels/configuration/)
- Docs: [Render hooks](/panels/render-hooks/), [Plugin development](/panels/plugins/), and the full **0.2.1 / #24 upgrade** section

**Upgrading from 0.2.1:** move inline `Panel.make(...)` from the provider into `app/orbit/admin_panel.py` as `register_admin_panel`, switch the provider to `register_app_orbit_panels(registry)`, keep `OrbitPanelProvider` in `config/app.py`, restart.

```bash title="terminal"
pip install -U 'almasix-orbit==0.3.0'
```

## 0.2.1

Packaging fix for Smith command loading ([#24](https://github.com/almasix-dev/almasix-orbit/issues/24)) plus Panel Configuration Filament 5 parity.

Highlights:

- **Fix #24** — Orbit wheels no longer ship a stub `almasix/__init__.py` that overwrote the framework init and dropped `almasix.__version__` (Smith “Command not loaded” warnings)
- Panel Configuration parity: `default`, `domain`, `home_url`, `favicon`, `brand_logo_height`, `theme_switcher`, `default_theme_mode`, `auth_middleware`, `boot_using`, `render_hook`, Plugin objects
- Docs: [render hooks](/panels/render-hooks/), [plugin development](/panels/plugins/), snippet path conventions
- Packaging regression test so the stub cannot return

### Upgrading existing apps (fix #24)

If you installed **Orbit 0.2.0** (or any build that shipped `almasix/__init__.py`), pip may have replaced the framework’s `almasix/__init__.py` with Orbit’s namespace stub. `smith version` / `list` / introspection then fail with:

```text
Command not loaded — … ImportError: cannot import name '__version__' from 'almasix'
```

`orbit:install` could still succeed; the warnings are the symptom.

**1. Upgrade Orbit packages to 0.2.1+**

```bash title="terminal"
pip install -U 'almasix-orbit==0.3.0'
```

(Or bump every `almasix-orbit-*` pin your app uses and reinstall.)

**2. Restore the framework `__init__.py`**

Upgrading Orbit removes the stub from *Orbit’s* wheel, but you still need the real Almasix init (with `__version__`) on disk. Force-reinstall the framework:

```bash title="terminal"
pip install -U --force-reinstall 'almasix>=0.6.0'
```

If you use a lockfile / uv / poetry, re-resolve so `almasix` is reinstalled after Orbit, then sync.

**3. Verify**

```bash title="terminal"
python -c "from almasix import __version__; print(__version__)"
smith version
```

You should see a version print and **no** `Command not loaded` lines for `version` / `list` / introspection. Then re-run `smith orbit:install` if you still need assets or the provider scaffold.

**Clean venv alternative:** recreate the virtualenv and install `almasix` + `almasix-orbit==0.3.0` fresh (framework first or together is fine — 0.2.1+ no longer overwrites the init).

**Plugin / package authors:** do not ship `almasix/__init__.py` in your wheels. Only contribute subpackages (see [Plugin development](/panels/plugins/)).

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
