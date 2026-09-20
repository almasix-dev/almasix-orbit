---
title: Panel configuration
description: Register an Orbit panel — brand, path, colors, resources, middleware, plugins, and the HTML shell.
---

A **panel** is the admin shell for your app: brand, URL path, navigation, middleware, and the list of resources / pages / widgets it owns. One Almasix app can register several panels (for example `admin` and `docs`) with different paths and contents.

## Where panels live

After `orbit:install`, configure panels in `app/orbit/{id}/panel.py`. Components for that panel live beside it under `resources/`, `pages/`, `widgets/`, and `themes/`. The app’s `OrbitPanelProvider` only discovers panel packages — it should not contain `Panel.make(...)`. Full layout: [Installation](/getting-started/installation/).

```python title="app/orbit/admin/panel.py"
from almasix.orbit import Panel, PanelRegistry, Plugin
from almasix.orbit.panels.hooks import register_render_hook


def register_admin_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("admin")
        .default()
        .path("orbit")                 # or .path("") / .path("/") for the site root
        # .domain("admin.example.com") # optional host binding
        .brand_name("Acme Admin")
        .brand_logo("/images/logo.svg")  # or asset("images/logo.svg") / "https://…"
        .brand_logo_dark("/images/logo-dark.svg")  # optional; falls back to light
        .brand_logo_height("2.25rem")
        # .brand_logo_only()
        # .brand_name_font_size("2rem")
        .favicon("images/favicon.svg")
        .font("Outfit")
        .primary("#f1511b")  # or .primary("info") / .colors(primary="#…", danger="#…")
        .content_max_width("screen-2xl")
        .simple_page_max_content_width("md")  # login / register bare shell
        .resources([PostResource, UserResource])
        .widgets([StatsOverview])
        # .middleware(["auth"])  # appends after default ["web"]
        # .auth_middleware(["auth"])  # authenticated routes only
        .login()                 # or .login(False) / .login(MyLogin)
        # .signup()              # opt-in registration (+ link on the login page)
        # .dashboard()           # on by default; .dashboard(False) or .dashboard(MyDashboard)
        .auth_guard("web")
        .dark_mode()
        .theme_switcher()
        .default_theme_mode("system")  # light | dark | system
        .sidebar_collapsible()
        # .home_url("/welcome")
        # .breadcrumbs_enabled(False)
        .discover_panel_dirs()   # resources|pages|widgets + themes/*.css
    )
    registry.register(panel)
    return panel
```

## Identity

| Method | Default | Notes |
|--------|---------|-------|
| `Panel.make(id)` | `"admin"` | Registry key via `panel.id` |
| `.default()` | `False` | Mark as the app default (`PanelRegistry.get_default()`) |
| `.path(...)` | `/{id}` | Leading `/` is added if missing; `""` or `"/"` mounts at root |
| `.domain(...)` | `None` | Host binding passed to Almasix `Router.add(domain=…)` |
| `.home_url(...)` | panel root | Brand link + breadcrumb home override |
| `.favicon(...)` | `None` | `<link rel="icon">` in the shell head |
| `.brand_name(...)` | `"Orbit"` | Document title; shown next to the logo unless logo-only |
| `.brand_logo(...)` | `None` | Light logo. Accepts `asset(...)`, absolute URLs, or bare relatives (resolved with `url()`). Optional `dark=` kwarg. |
| `.brand_logo_dark(...)` | light logo | Dark-mode logo; falls back to the light logo when unset |
| `.brand_logo_height(...)` | `"2rem"` | CSS height (`--or-brand-logo-height`) |
| `.brand_logo_only()` | `False` | Hide the brand name when a logo is set |
| `.brand_name_font_size(...)` | `"1.8rem"` | Font size for the visible brand name (shell + login). Any CSS length |
| `.font(...)` | `"Outfit"` | Shell typography |
| `.primary(...)` | `"#f1511b"` | Brand primary (hex or semantic token like `"info"`). Soft/deep accents derive automatically |
| `.colors(**tokens)` | `primary="#f1511b"` | Merge semantic colors (`primary`, `danger`, `success`, `warning`, `info`, `gray`). Values may be hex or tokens |
| `.content_max_width(...)` | `"screen-2xl"` | Cap centered page content (`screen-2xl` → `96rem`) |
| `.simple_page_max_content_width(...)` | `"lg"` | Max width for bare auth pages |

Toggle-style methods take `condition: bool = True` (e.g. `.dark_mode()`, `.sidebar_collapsible()`, `.theme_switcher()`).

Auth and home pages accept `True`, `False`, or a custom `Page` subclass:

| Value | Meaning |
|-------|---------|
| `True` / no args | Use Orbit’s built-in page (`Login`, `Register`, or `Dashboard`) |
| `False` | Disable that page |
| A `Page` subclass | Use your custom page instead |

```python title="app/orbit/admin/panel.py"
from almasix.orbit import Login, Register, Dashboard

class MyLogin(Login):
    title = "Welcome back"

panel.login(MyLogin).signup().dashboard()
```

## Contents

| Method | What it stores |
|--------|----------------|
| `.resources([...])` | Resource classes (replaces the list) |
| `.pages([...])` | Custom page classes |
| `.widgets([...])` | Dashboard widgets |
| `.middleware([...])` | **Appends** after default `["web"]` (deduped). Use `replace=True` to set the stack explicitly |
| `.auth_middleware([...])` | Extra middleware on authenticated routes only (not login/register) |
| `.login(...)` | Default `True` → built-in `Login`. Pass `False` or a custom page class |
| `.signup(...)` | Default `False`. Pass `True`/`()` for `Register`, or a custom page. Adds login↔signup links |
| `.dashboard(...)` | Default `True` → built-in `Dashboard` as panel home (`/`). Pass `False` to use the first resource instead |
| `.auth_guard("web")` | Guard name |
| `.dark_mode()` | Enable dark-mode CSS / preference boot |
| `.theme_switcher()` | Show the light/dark/system toggle (requires dark mode) |
| `.default_theme_mode(...)` | `"system"` / `"light"` / `"dark"` when the user has no stored choice |
| `.sidebar_collapsible()` | Off by default. Pass `True` (or call with no args) to show the collapse control |
| `.breadcrumbs_enabled()` | On by default; pass `False` to hide the trail |
| `.plugin(...)` / `.plugins([...])` | Callable **or** `Plugin` instance (`register` → callbacks → `boot`). **Only** way to load plugins — no `{id}/plugins` autodisc. |
| `.boot_using(fn)` | Runs after plugins when the panel mounts |
| `.render_hook(name, fn)` | Panel-scoped HTML injection (see hooks below) |
| `.theme_package(...)` | Load `*.css` from dotted packages (also wired by `.discover_panel_dirs()` → `{pkg}.themes`) |
| `.theme_stylesheet(...)` | Extra `<link rel="stylesheet">` URLs in the shell head |

### Discovery paths

Prefer the colocated helper (scaffolding emits this):

```python
panel = Panel.make("admin").discover_panel_dirs()
# → app.orbit.admin.resources|pages|widgets
# → theme CSS from app.orbit.admin.themes
```

Put overrides in `app/orbit/admin/themes/custom.css` (any `*.css` under `themes/`). Files are inlined as `<style data-orbit-theme="…">` after Orbit’s core CSS.

Shared custom fields live under `app/orbit/shared/fields/` (`make:orbit-field`). Shared resources under `app/orbit/shared/resources/` must be registered explicitly on every panel that uses them — they are never auto-discovered.

Or pass directories / packages explicitly. ``mount_panel`` calls ``load_discovered()`` for you; call it yourself only when you need the classes before mount.

```python
from almasix import app_path
# or: from almasix.support import app_path

panel = (
    Panel.make("admin")
    .discover_resources(app_path("orbit", "admin", "resources"))
    .discover_pages("app.orbit.admin.pages")
    .discover_widgets("app.orbit.admin.widgets")
)
```

Paths may be:

| Form | Example |
|------|---------|
| Absolute FS dir (preferred with ``app_path``) | ``app_path("orbit", "admin", "resources")`` |
| Dotted package | ``"app.orbit.admin.resources"`` |
| Relative dir (only if it exists vs process cwd) | ``"app/orbit/admin/resources"`` |

Discovered classes are merged with any you still register via ``.resources([...])``. Deduplication uses the fully-qualified class name so two panels may each define ``PostResource``.

## Plugins and render hooks

```python
from almasix.orbit.panels.hooks import Plugin, PANEL_HOOKS

class BrandingPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__("branding")

    def register(self, panel: Panel) -> None:
        panel.favicon("images/favicon.svg")

    def boot(self, panel: Panel) -> None:
        panel.render_hook(
            "panels::styles.after",
            lambda **_ctx: "<!-- branding plugin -->\n",
        )

panel = (
    Panel.make("admin")
    .plugin(BrandingPlugin())
    .plugin(lambda p: None)  # legacy callable still supported
    .boot_using(lambda p: None)
    .render_hook("panels::head.end", lambda **_ctx: '<meta name="orbit" content="1" />\n')
)
```

Hooks run at mount via ``panel.run_plugins()`` (also called by ``mount_registered_panels``). Common positions live in ``PANEL_HOOKS`` (`panels::head.*`, `body.*`, `sidebar.nav.*`, `topbar.*`, `content.*`, …).

Full guides: [Render hooks](/panels/render-hooks/), [Plugin development](/panels/plugins/).

## Registry

```python
registry = app.make(PanelRegistry)
registry.register(panel)
registry.get("admin")        # Panel | None
registry.get_default()       # panel marked .default(), else first registered
registry.default("admin")    # mark an already-registered panel as default
registry.all()               # list[Panel]
```

`OrbitServiceProvider` binds `PanelRegistry` as a singleton.

## Navigation

```python
items = panel.navigation_items()
# [{label, icon, group, subgroup, url, sort}, ...]
```

Items come from each resource and page’s navigation class vars, plus custom `NavigationItem`s, sorted by `navigation_sort`. Layout helpers: `.apps_navigation()`, `.sidebar_navigation()`, `.top_navigation()` (or `.navigation_layout(...)`). Full guide: [Navigation](/navigation/overview/).

User menu / notifications APIs on `Panel` are covered under [User menu](/navigation/user-menu/) and notifications docs.

Actions on the shell (modal vs URL, `mountAction`): [Panel actions](/panels/actions/).

## The shell

```python
html = panel.render_shell(content_html, user=request.user)
```

You get a full HTML document: sidebar, brand, favicon, theme boot, and links to `/vendor/orbit/orbit.css` + `orbit.js`. Pass the authenticated user so permission-aware nav can filter itself. Auth pages use `bare=True` and `.simple_page_max_content_width(...)`.

## Multiple panels

Need a public “docs” panel and a private “admin” panel? Make two IDs, register both, and route to the one you want:

```python
Panel.make("admin").default().path("admin").resources([PostResource])
Panel.make("docs").path("docs").resources([ArticleResource]).login(False)
```

See `examples/orbit-admin/app/providers/orbit_panel_provider.py` for a live multi-panel + plugin showcase.

Next: [Resources](/resources/overview/).

## Preview

![Panel shell (light)](/examples/light/panels/shell.png)

![Panel shell (dark)](/examples/dark/panels/shell.png)
