---
title: Installation
description: Install almasix-orbit, scaffold colocated panels under app/orbit/{id}/, and confirm the thin provider.
---

Orbit lives in its own package — [`almasix-orbit`](https://pypi.org/project/almasix-orbit/) — so you can add an admin panel without dragging it into every Almasix app by default.

## Requirements

- [Almasix](https://docs.almasix.com/)
- [`almasix-conduit`](https://conduit.almasix.com/)
- [`almasix-permission`](https://pypi.org/project/almasix-permission/) (for the default auth/permission middleware story)

## Install

```bash title="terminal"
pip install almasix-orbit
smith orbit:install
```

That command:

1. Publishes Orbit CSS/JS and writes `config/orbit.py`
2. Creates the default panel package at `app/orbit/admin/` (id/path overridable with `--panel` / `--path`)
3. Writes a **thin** `app/providers/orbit_panel_provider.py` whose only job is discovery
4. Lists that provider in `config/app.py`

After install, open `/admin` (or whatever `--path` you chose). Restart `smith serve` if the process was already running.

## Layout: panels vs provider

Orbit expects this split (v0.3+):

| Path | Responsibility |
|------|----------------|
| `app/orbit/{id}/panel.py` | **Define** the panel — brand, path, resources, pages, plugins. Export `register_{id}_panel(registry)`. |
| `app/orbit/{id}/resources\|pages\|widgets\|themes/` | Components **owned by that panel**. Resources/pages/widgets + theme CSS via `.discover_panel_dirs()`. |
| `app/orbit/shared/` | Shared code (`fields/`, `resources/`, …) — **never** auto-discovered; import and register explicitly. |
| `app/providers/orbit_panel_provider.py` | **Register** panels — call `register_app_orbit_panels(...)`. Do not put `Panel.make(...)` here. |
| `config/app.py` | List `OrbitPanelProvider` under `providers` so discovery runs on boot. |

```text
app/
  orbit/
    __init__.py
    admin/
      panel.py              ← Panel.make("admin") …
      resources/
      pages/
      widgets/
      themes/               ← *.css inlined by discover_panel_dirs
    app/                    ← optional second panel
      panel.py
      resources/
    shared/                 ← optional; explicit register only
      fields/               ← make:orbit-field writes here
      resources/
  providers/
    orbit_panel_provider.py ← thin: discover only
```

### Panel file (where you configure)

```python title="app/orbit/admin/panel.py"
from almasix.orbit import Panel, PanelRegistry


def register_admin_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .navigation_layout("apps")
        .login()
        .discover_panel_dirs()
    )
    registry.register(panel)
    return panel
```

### Provider (discovery only)

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import PanelRegistry
from almasix.orbit.panels.discover import register_app_orbit_panels
from almasix.providers import ServiceProvider


class OrbitPanelProvider(ServiceProvider):
    def boot(self) -> None:
        register_app_orbit_panels(self.app.make(PanelRegistry))
```

### `config/app.py`

```python title="config/app.py"
"providers": [
    "app.providers.app_service_provider.AppServiceProvider",
    "app.providers.orbit_panel_provider.OrbitPanelProvider",
],
```

`OrbitServiceProvider` (package entry-point) mounts whatever is already in `PanelRegistry`. Your app provider is what **fills** the registry from `app/orbit`.

## Discovery rules

`register_app_orbit_panels` loads every `app.orbit.<id>.panel` module and calls `register_{id}_panel(registry)`:

| Path | Function called |
|------|-----------------|
| `app/orbit/admin/panel.py` | `register_admin_panel` |
| `app/orbit/app/panel.py` | `register_app_panel` |
| `app/orbit/shop/panel.py` | `register_shop_panel` |

Orbit 0.4 dropped `app/orbit/{id}_panel.py`. Panels live at `app/orbit/{id}/panel.py` only.

`.discover_panel_dirs()` (emitted by scaffolding) points discovery at `{panel_pkg}.resources` / `.pages` / `.widgets` and loads `*.css` from `{panel_pkg}.themes`. You can still call `.resources([...])` explicitly or pass custom paths to `.discover_resources(...)`.

**Plugins** are never auto-discovered — only `.plugin(...)` / `.plugins([...])` in `panel.py`.

**Cross-panel resources:** put the class under `app/orbit/shared/resources/` (or anywhere) and register it explicitly on each panel that needs it (`.resources([SharedPostResource])`). Autodiscovery only covers the panel’s own package tree.

## Add another panel

```bash title="terminal"
smith make:orbit-panel app --path=app   # alias: smith orbit:panel …
```

That writes `app/orbit/app/panel.py` plus empty component dirs. The thin provider already discovers it — no provider edit. Restart `smith serve`, then open `/app`.

Other generators (panel-scoped):

```bash title="terminal"
smith make:orbit-resource Post --panel=admin
smith make:orbit-resource Post --panel=admin --model=Post --generate
smith make:orbit-page Settings --panel=admin
smith make:orbit-widget StatsOverview --panel=admin
smith make:orbit-field MoneyInput             # app/orbit/shared/fields/
smith make:orbit-plugin AuditLog --vendor=acme --author=jane   # third-party package + listing YAML
```

`--generate` inspects the model’s database columns (when the table exists) and stubs matching form fields and table columns for you.
With more than one panel, omit `--panel` in an interactive terminal and Smith asks which panel to use. Under `--no-interaction` / CI it picks `admin` when present, otherwise the first panel id.

## Troubleshooting 404s

If `/admin` or `/app` 404s:

1. `config/app.py` lists `OrbitPanelProvider`
2. `app/orbit/{id}/panel.py` exists and defines `register_{id}_panel`
3. You restarted after scaffolding

Panels mount on a **path prefix** only — existing host routes (for example `/`) stay put unless you set `.path("/")`.

## Migrating from 0.2.x

1. Move `admin_panel.py` → `admin/panel.py` (keep `register_admin_panel`)
2. Move panel-owned resources/pages/widgets under `admin/{resources,pages,widgets}/`
3. Put truly shared classes under `shared/` and register them explicitly
4. Add `.discover_panel_dirs()` (or rely on auto-wire when discover paths are empty)
5. Keep the thin provider; restart

## Imports

The meta-package pulls panels plus orbit siblings (forms, tables, actions, …). Import paths always start with `almasix.orbit`:

```python
from almasix.orbit import Panel, PanelRegistry, Resource, Page
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn
```

Source: [`almasix-dev/almasix-orbit`](https://github.com/almasix-dev/almasix-orbit).

## Optional assets

Want a local copy of the CSS/JS to poke at?

```bash title="terminal"
smith vendor:publish --tag=orbit-assets
```

That drops `public/vendor/orbit/orbit.css` and `orbit.js`. The panel shell already links those paths — publish when you’re ready to vendor or tweak. `orbit:install` can run this for you.

Prism layouts that host Orbit UI can also use:

```html title="resources/views/layouts/app.prism.html"
@orbitStyles
@orbitScripts
```

Those directives set `__orbit_styles` / `__orbit_scripts` in the Prism context when the engine is bound.

## Defaults

On register, the provider seeds in-memory config if nothing is set yet:

```python
{
    "path": "/admin",
    "font": "Outfit",
    "brand": "Orbit",
}
```

Tune brand, path, and colors on the `Panel` instance in `app/orbit/{id}/panel.py` — see [Panel configuration](/panels/configuration/). Interactive pages are Conduit hosts; SDUI forms/tables paint into those hosts.

Next up: [Quick start](/getting-started/quick-start/).
