---
title: Release notes
description: What’s new in Orbit — major and minor highlights.
---

Orbit follows Almasix’s major-line docs model. This page tracks notable
changes; pin a package version in production and read the matching line in the
header switcher.

## Unreleased (`main`)

Working from the tip of `main`? Switch the docs to **main** in the header.
Breaking changes will land here before they become a new major.

### Per-panel component directories ([#32](https://github.com/almasix-dev/almasix-orbit/issues/32))

**Breaking (targets 0.3.0):** each panel owns its components under `app/orbit/{id}/`.

- `orbit:install` / `make:orbit-panel` → `app/orbit/{id}/panel.py` + `resources/`, `pages/`, `widgets/`, `themes/` (stub `custom.css`)
- `make:orbit-resource|page|widget --panel=` writes into that panel’s tree
- `make:orbit-field` → `app/orbit/shared/fields/` (never auto-discovered)
- `.discover_panel_dirs()` discovers resources/pages/widgets **and** loads `themes/*.css`; FQCN dedupe; legacy `*_panel.py` still loads with `DeprecationWarning`
- `.theme_package(...)` / `.theme_stylesheet(...)` for extra theme CSS
- Plugins **only** via `.plugin(...)` — no `{id}/plugins` autodisc
- Shared resources: explicit `.resources([...])` on each panel; `app/orbit/shared/` is never auto-pulled
- Thin provider unchanged; examples migrated to colocated layout

See [Installation](/getting-started/installation/) for the upgrade path from flat `app/orbit/resources`.

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
pip install -U 'almasix-orbit==0.2.2'
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
pip install -U 'almasix-orbit==0.2.2'
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

**Clean venv alternative:** recreate the virtualenv and install `almasix` + `almasix-orbit==0.2.2` fresh (framework first or together is fine — 0.2.1+ no longer overwrites the init).

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

## Unreleased (`main`)

Working from the tip of `main`? Switch the docs to **main** in the header.
Breaking changes will land here before they become a new major.
