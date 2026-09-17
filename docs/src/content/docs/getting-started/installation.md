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
```

That pulls the panels meta-package and its orbit siblings (forms, tables, actions, …). Import paths always start with `almasix.orbit`:

```python
from almasix.orbit import Panel, PanelRegistry, Resource, Page
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn
```

`OrbitServiceProvider` is discovered automatically through the `almasix.providers` entry-point group. No manual provider registration for the happy path.

Source: [`almasix-dev/almasix-orbit`](https://github.com/almasix-dev/almasix-orbit).

## Optional assets

Want a local copy of the CSS/JS to poke at?

```bash title="terminal"
smith vendor:publish --tag=orbit-assets
```

That drops `public/vendor/orbit/orbit.css` and `orbit.js`. The panel shell already links `/vendor/orbit/orbit.css` and `/vendor/orbit/orbit.js` — publish when you’re ready to vendor or tweak.

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
    "path": "/orbit",
    "font": "Outfit",
    "brand": "Orbit",
}
```

Tune brand, path, and colors on the `Panel` instance itself — see [Configuration & assets](/configuration/).

Next up: [Quick start](/getting-started/quick-start/).
