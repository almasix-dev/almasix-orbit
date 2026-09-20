---
title: Plugin development
description: Build, publish, and register Orbit plugins — Panel Plugin classes, package layout, and use inside or outside panels.
---

An Orbit **plugin** is a small package (or app module) that configures one or more panels — brand, hooks, resources, middleware — without editing every consumer’s panel file.

Subclass `Plugin` and implement two hooks:

- **`register`** — mutate the panel early (brand, colors, resources, …)
- **`boot`** — run at mount time for side effects (render hooks, routes, discovery)

That split keeps config changes separate from “do something when the panel mounts.”

## Anatomy

```python title="my_orbit_plugin/plugin.py"
from typing import Any

from almasix.orbit.panels.hooks import Plugin
from almasix.orbit.panels.panel import Panel


class AcmeBrandingPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__("acme-branding")

    def register(self, panel: Panel) -> None:
        """Mutate panel config before routes mount."""
        panel.brand_name("Acme Admin")
        panel.favicon("vendor/acme/favicon.svg")
        panel.primary("#0ea5e9")

    def boot(self, panel: Panel) -> None:
        """Side effects at mount — hooks, discovery, etc."""
        panel.render_hook(
            "panels::styles.after",
            lambda **_ctx: '  <link rel="stylesheet" href="/vendor/acme/acme.css" />\n',
        )
```

Lifecycle when the app boots:

1. Your provider builds a `Panel` and calls `.plugin(AcmeBrandingPlugin())` (or `.plugins([...])`).
2. `mount_registered_panels` → `panel.run_plugins()`:
   - every plugin’s `register(panel)`
   - legacy callable plugins (if any)
   - every plugin’s `boot(panel)`
   - every `.boot_using` callback
3. `mount_panel` loads discovery paths and registers routes.

**Orbit does not auto-discover plugins** from `app/orbit/{id}/plugins/` (or anywhere else). Keep plugin modules next to the panel if you like, but always wire them with `.plugin(...)` / `.plugins([...])` in `panel.py`.

Legacy callables still work:

```python title="app/providers/orbit_panel_provider.py"
panel.plugin(lambda p: p.sidebar_collapsible())
```

Prefer `Plugin` subclasses for anything you publish.

## Using a plugin in an app

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel, PanelRegistry
from almasix.providers import ServiceProvider
from my_orbit_plugin import AcmeBrandingPlugin
from app.orbit.resources.post_resource import PostResource


class OrbitPanelProvider(ServiceProvider):
    def boot(self) -> None:
        panel = Panel.make("admin").path("admin").plugin(AcmeBrandingPlugin()).resources(
            [PostResource]
        )
        self.app.make(PanelRegistry).register(panel)
```

Multiple plugins:

```python title="app/providers/orbit_panel_provider.py"
panel.plugins(
    [
        AcmeBrandingPlugin(),
        BillingPlugin(),
    ]
)
```

Order matters: `register` runs in list order, then `boot` in the same order.

## Package layout (publishable)

Minimal PyPI-ready layout:

```text
acme-orbit-branding/
  pyproject.toml
  README.md
  src/
    acme_orbit_branding/
      __init__.py          # export AcmeBrandingPlugin
      plugin.py
      assets/              # optional CSS / favicon to publish
```

```toml title="pyproject.toml"
[project]
name = "acme-orbit-branding"
version = "0.1.0"
dependencies = [
  "almasix-orbit>=0.3.0",
]

[project.entry-points."almasix.providers"]
# optional — only if the plugin should auto-boot as a ServiceProvider
# acme_orbit = "acme_orbit_branding.provider:AcmeOrbitProvider"
```

```python title="src/acme_orbit_branding/__init__.py"
from acme_orbit_branding.plugin import AcmeBrandingPlugin

__all__ = ["AcmeBrandingPlugin"]
```

Publish like any Python package (`hatchling` / `setuptools`, then `twine upload`). Consumers:

```bash title="terminal"
pip install acme-orbit-branding
```

Do **not** ship an `almasix/__init__.py` stub in your wheel — that overwrites the framework namespace (see issue #24). Only add packages under your own top-level name, or under `almasix.orbit_plugins…` if you intentionally extend Orbit’s namespace without a root init file.

## Optional: ServiceProvider auto-discovery

If the plugin should register a panel (or several) without the app touching `OrbitPanelProvider`, expose an Almasix provider entry-point:

```python title="src/acme_orbit_branding/provider.py"
from almasix.orbit import Panel, PanelRegistry
from almasix.providers import ServiceProvider
from acme_orbit_branding.plugin import AcmeBrandingPlugin


class AcmeOrbitProvider(ServiceProvider):
    def boot(self) -> None:
        registry = self.app.make(PanelRegistry)
        existing = registry.get("admin")
        if existing is not None:
            existing.plugin(AcmeBrandingPlugin())
            return
        panel = Panel.make("admin").path("admin").plugin(AcmeBrandingPlugin())
        registry.register(panel)
```

Most plugins should stay **passive** (`.plugin(...)` in the app) so hosts keep control of panel ids and paths.

## Outside panels

`Plugin` is panel-oriented, but the same package can export plain helpers for standalone forms/tables:

```python title="src/acme_orbit_branding/forms.py"
from almasix.orbit.forms import TextInput

def acme_title_field() -> TextInput:
    return TextInput.make("title").label("Title").required()
```

Use those helpers from resources or from non-panel Conduit hosts. Render hooks and `Panel.plugin` only apply when a panel shell mounts.

## Checklist

- [ ] Subclass `Plugin`, unique `get_id`
- [ ] Keep `register` pure (mutate panel); put I/O and hooks in `boot`
- [ ] Scope render hooks to the panel id
- [ ] No `almasix/__init__.py` in the published wheel
- [ ] Document the one-liner: `panel.plugin(YourPlugin())`
- [ ] Add a smoke test that `run_plugins` calls `register` then `boot`

## Related

- [Render hooks](/panels/render-hooks/) — positions and scoping
- [Panel configuration](/panels/configuration/) — fluent panel API
- [Packages](/packages/) — Orbit’s own PyPI map
