---
title: Installation
description: Install almasix-orbit, confirm the provider, and publish optional assets.
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

`orbit:install` publishes assets, writes `config/orbit.py`, scaffolds the
default panel at `app/orbit/{id}_panel.py`, a thin `OrbitPanelProvider` that
**discovers** every `app/orbit/*_panel.py`, and registers that provider in
`config/app.py`.

Scaffold more surfaces with Smith (canonical `make:orbit-*` names; `orbit:*` aliases work the same):

```bash title="terminal"
smith make:orbit-panel app --path=app   # alias: smith orbit:panel …
smith make:orbit-resource Post --panel=admin  # alias: smith orbit:resource …
smith make:orbit-field MoneyInput             # alias: smith orbit:field …
smith serve
```

`make:orbit-panel` only adds another `app/orbit/{id}_panel.py`. The provider
picks it up automatically on the next boot — restart `smith serve`.

## Provider vs panels in `app/orbit`

| Piece | Role |
|-------|------|
| `app/orbit/{id}_panel.py` | **Defines** a panel (`register_{id}_panel`). This is where brand, path, resources, etc. live. |
| `OrbitPanelProvider` | Thin app provider. Calls `register_app_orbit_panels(...)` to load every `*_panel.py` under `app/orbit`. Must be listed in `config/app.py`. |
| `OrbitServiceProvider` | Package entry-point (auto-discovered). Mounts whatever is already in the registry. |

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import PanelRegistry
from almasix.orbit.panels.discover import register_app_orbit_panels
from almasix.providers import ServiceProvider


class OrbitPanelProvider(ServiceProvider):
    def boot(self) -> None:
        register_app_orbit_panels(self.app.make(PanelRegistry))
```

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

Typical `config/app.py`:

```python title="config/app.py"
"providers": [
    "app.providers.app_service_provider.AppServiceProvider",
    "app.providers.orbit_panel_provider.OrbitPanelProvider",
],
```

If `/admin` or `/app` 404s, check that list and that `app/orbit/*_panel.py` exists, then restart `smith serve`.

Panels mount on a **path prefix** only — existing host routes (for example `/`) are left alone unless you intentionally set `.path("/")`.

That pulls the panels meta-package and its orbit siblings (forms, tables, actions, …). Import paths always start with `almasix.orbit`:

```python
from almasix.orbit import Panel, PanelRegistry, Resource, Page
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn
```

`OrbitServiceProvider` is discovered automatically through the `almasix.providers` entry-point group. `orbit:install` / `orbit:panel` also register `OrbitPanelProvider` in `config/app.py` when they can patch the file.

Source: [`almasix-dev/almasix-orbit`](https://github.com/almasix-dev/almasix-orbit).

## Optional assets

Want a local copy of the CSS/JS to poke at?

```bash title="terminal"
smith vendor:publish --tag=orbit-assets
```

That drops `public/vendor/orbit/orbit.css` and `orbit.js`. The panel shell already links `/vendor/orbit/orbit.css` and `/vendor/orbit/orbit.js` — publish when you’re ready to vendor or tweak. `orbit:install` can run this for you.

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

Tune brand, path, and colors on the `Panel` instance itself — see [Configuration & assets](/configuration/). Interactive pages are Conduit hosts (Livewire analogue); SDUI forms/tables paint into those hosts.

Next up: [Quick start](/getting-started/quick-start/).
