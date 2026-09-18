---
title: Installation
description: Install almasix-orbit, scaffold panels under app/orbit, and confirm the thin provider.
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
2. Creates the default panel at `app/orbit/admin_panel.py` (id/path overridable with `--panel` / `--path`)
3. Writes a **thin** `app/providers/orbit_panel_provider.py` whose only job is discovery
4. Lists that provider in `config/app.py`

After install, open `/admin` (or whatever `--path` you chose). Restart `smith serve` if the process was already running.

## Layout: panels vs provider

Orbit expects this split:

| Path | Responsibility |
|------|----------------|
| `app/orbit/{id}_panel.py` | **Define** the panel — brand, path, resources, pages, plugins. Export `register_{id}_panel(registry)`. |
| `app/providers/orbit_panel_provider.py` | **Register** panels — call `register_app_orbit_panels(...)`. Do not put `Panel.make(...)` here. |
| `config/app.py` | List `OrbitPanelProvider` under `providers` so discovery runs on boot. |

```text
app/
  orbit/
    __init__.py
    admin_panel.py      ← Panel.make("admin") …
    app_panel.py        ← optional second panel
    resources/          ← resources, pages, widgets, …
  providers/
    orbit_panel_provider.py   ← thin: discover only
```

### Panel file (where you configure)

```python title="app/orbit/admin_panel.py"
from almasix.orbit import Panel, PanelRegistry


def register_admin_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("admin")
        .path("admin")
        .brand_name("Orbit")
        .navigation_layout("apps")
        .login()
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

`register_app_orbit_panels` imports every top-level module under `app.orbit` whose name ends in `_panel`, then calls `register_{id}_panel(registry)`:

| File | Function called |
|------|-----------------|
| `app/orbit/admin_panel.py` | `register_admin_panel` |
| `app/orbit/app_panel.py` | `register_app_panel` |
| `app/orbit/shop_panel.py` | `register_shop_panel` |

Resources, pages, and widgets are **not** auto-registered as panels. Put them on the panel inside your `register_*_panel` (e.g. `.resources([...])`), or use the panel’s discover helpers documented under [Panel configuration](/panels/configuration/).

## Add another panel

```bash title="terminal"
smith make:orbit-panel app --path=app   # alias: smith orbit:panel …
```

That only writes `app/orbit/app_panel.py`. The thin provider already discovers it — no provider edit. Restart `smith serve`, then open `/app`.

Other generators:

```bash title="terminal"
smith make:orbit-resource Post --panel=admin  # alias: smith orbit:resource …
smith make:orbit-field MoneyInput             # alias: smith orbit:field …
```

## Troubleshooting 404s

If `/admin` or `/app` 404s:

1. `config/app.py` lists `OrbitPanelProvider`
2. `app/orbit/{id}_panel.py` exists and defines `register_{id}_panel`
3. You restarted after scaffolding

Panels mount on a **path prefix** only — existing host routes (for example `/`) stay put unless you set `.path("/")`.

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

Tune brand, path, and colors on the `Panel` instance in `app/orbit/*_panel.py` — see [Panel configuration](/panels/configuration/). Interactive pages are Conduit hosts; SDUI forms/tables paint into those hosts.

Next up: [Quick start](/getting-started/quick-start/).
