---
title: Render hooks
description: Inject HTML into the Orbit panel shell at named positions — head, body, sidebar, topbar, content, and more.
---

**Render hooks** let you inject HTML into the panel shell without forking Orbit’s templates. Register a callback for a named position; when the shell renders, Orbit concatenates every matching callback’s return value into that slot.

Use them for small, targeted HTML — scripts, meta tags, banners, analytics snippets, or third-party widgets — at well-known points in the document (`panels::head.end`, `panels::content.start`, and so on).

## How they work

```mermaid
flowchart TD
  register[register_render_hook or panel.render_hook] --> store["_HOOKS registry"]
  render[panel.render_shell] --> call["render_hook(name, scope=panel.id)"]
  store --> call
  call --> html[HTML string spliced into shell]
```

1. **Register** a callback with `register_render_hook(name, callback, scopes=...)` or the fluent `panel.render_hook(name, callback)`.
2. The callback must return a **string** (HTML). It may accept `**ctx` — Orbit passes `scope` and often `user` depending on the position.
3. When `render_shell` runs, it calls `render_hook(name, scope=panel.id, ...)` at each position and inserts the concatenated HTML.

Hooks are **process-global**. Prefer scoping them to a panel id so a second panel does not inherit the first panel’s injections.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit.panels.hooks import register_render_hook, clear_render_hooks

# Panel-scoped (recommended)
panel.render_hook(
    "panels::head.end",
    lambda **_ctx: '  <meta name="app-panel" content="admin" />\n',
)

# Equivalent global registration with an explicit scope list
register_render_hook(
    "panels::head.end",
    lambda **_ctx: '  <meta name="app-panel" content="admin" />\n',
    scopes=["admin"],
)
```

`panel.render_hook(...)` defaults `scopes` to `[panel.id]`. Pass `scopes=None` only when you intentionally want every panel.

### Clearing hooks

Tests (and rare reset paths) can wipe the registry:

```python title="tests/test_render_hooks.py"
from almasix.orbit.panels.hooks import clear_render_hooks

def setup_function() -> None:
    clear_render_hooks()
```

## Hook positions

Built-in names live in `PANEL_HOOKS` (`almasix.orbit.panels.hooks`). Use these strings exactly:

| Position | Where it lands |
|----------|----------------|
| `panels::head.start` | Early in `<head>` (after charset / viewport / title boot) |
| `panels::head.end` | End of `<head>` |
| `panels::styles.after` | After Orbit’s CSS / inline theme `<style>` |
| `panels::scripts.after` | End of `<body>`, after Alpine |
| `panels::body.start` | Start of `<body>` content (before app / auth shell) |
| `panels::body.end` | End of body wrap (after app / auth shell) |
| `panels::sidebar.nav.start` | Before sidebar `<nav>` |
| `panels::sidebar.nav.end` | After sidebar `<nav>` |
| `panels::topbar.start` | Inside topbar start cluster |
| `panels::topbar.end` | Inside topbar end cluster |
| `panels::content.start` | Before breadcrumbs + `<main>` |
| `panels::content.end` | After `<main>` |
| `panels::global-search.before` | Before the global-search slot |
| `panels::global-search.after` | After the global-search slot |
| `panels::user-menu.before` | Before the user menu |
| `panels::user-menu.after` | After the user menu |

You may register custom names too — they only fire if something calls `render_hook` with that name. Stick to `PANEL_HOOKS` unless you control the caller.

## Examples

### Meta tags and analytics

```python title="app/providers/orbit_panel_provider.py"
panel = Panel.make("admin").path("admin").brand_name("Acme")

panel.render_hook(
    "panels::head.end",
    lambda **_ctx: (
        '  <meta name="theme-color" content="#f1511b" />\n'
        '  <script defer src="https://example.test/analytics.js"></script>\n'
    ),
)
```

### Custom CSS after Orbit’s stylesheet

```python title="app/providers/orbit_panel_provider.py"
panel.render_hook(
    "panels::styles.after",
    lambda **_ctx: '  <link rel="stylesheet" href="/css/admin-tweaks.css" />\n',
)
```

### Banner above page content

```python title="app/providers/orbit_panel_provider.py"
def maintenance_banner(*, user=None, **_ctx) -> str:
    if user is None:
        return ""
    return (
        '<div class="or-callout or-callout-warning" role="status">'
        "Scheduled maintenance tonight 22:00 UTC."
        "</div>\n"
    )

panel.render_hook("panels::content.start", maintenance_banner)
```

### Sidebar promo link

```python title="app/providers/orbit_panel_provider.py"
panel.render_hook(
    "panels::sidebar.nav.end",
    lambda **_ctx: (
        '<a class="or-nav-link" href="https://docs.example.test">'
        "<span>Docs</span></a>\n"
    ),
)
```

## Scoping rules

| Registration | Fires when |
|--------------|------------|
| `scopes=None` / omitted on `register_render_hook` | Every `render_hook` call for that name |
| `scopes=["admin"]` | Only when `scope="admin"` (the panel id) |
| `panel.render_hook(...)` | Defaults to that panel’s id |

Bare auth pages (`render_shell(..., bare=True)`) still run `body.*` hooks; sidebar/topbar hooks are skipped because that chrome is not rendered.

## Related

- Wire hooks from a reusable package: [Plugin development](/panels/plugins/)
- Panel fluent surface: [Panel configuration](/panels/configuration/)
