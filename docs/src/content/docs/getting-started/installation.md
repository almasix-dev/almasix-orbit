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

`orbit:install` publishes assets, writes `config/orbit.py`, scaffolds
`app/providers/orbit_panel_provider.py`, and **adds that provider to
`config/app.py`**. Panels only mount when that provider boots — a panel stub
file alone does nothing.

Scaffold more surfaces with Smith (canonical `make:orbit-*` names; `orbit:*` aliases work the same):

```bash title="terminal"
smith make:orbit-panel app --path=app   # alias: smith orbit:panel …
smith make:orbit-resource Post --panel=admin  # alias: smith orbit:resource …
smith make:orbit-field MoneyInput             # alias: smith orbit:field …
smith serve
```

`make:orbit-panel` writes `app/orbit/{id}_panel.py` **and** wires
`register_{id}_panel(...)` into `OrbitPanelProvider.boot`. Restart the server
after scaffolding.

## Provider vs panel stub

| Piece | Role |
|-------|------|
| `OrbitPanelProvider` | App service provider. **Must** be listed in `config/app.py` `providers`. Its `boot` registers panels on `PanelRegistry`. |
| `app/orbit/{id}_panel.py` | Optional helper that builds one panel (`register_{id}_panel`). Only runs if the provider calls it. |
| `OrbitServiceProvider` | Package entry-point (auto-discovered). Mounts whatever is already in the registry. |

Typical `config/app.py`:

```python title="config/app.py"
"providers": [
    "app.providers.app_service_provider.AppServiceProvider",
    "app.providers.orbit_panel_provider.OrbitPanelProvider",
],
```

If `/admin` or `/app` 404s, check that list first, then restart `smith serve`.

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
