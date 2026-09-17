---
title: Panel configuration
description: Register an Orbit panel — brand, path, colors, resources, middleware, and the HTML shell.
---

A **panel** is the admin shell: brand, path, navigation, middleware, and the list of resources / pages / widgets it owns.

```python
from almasix.orbit import Panel, PanelRegistry

panel = (
    Panel.make("admin")
    .path("orbit")
    .brand_name("Acme Admin")
    .brand_logo("/images/logo.svg")
    .font("Outfit")
    .colors(primary="#f1511b")
    .resources([PostResource, UserResource])
    .pages([DashboardPage])
    .widgets([StatsOverview])
    .middleware(["auth", "permission"])
    .login()
    .auth_guard("web")
    .dark_mode()
    .sidebar_collapsible()
)

app.make(PanelRegistry).register(panel)
```

## Identity

| Method | Default | Notes |
|--------|---------|-------|
| `Panel.make(id)` | `"admin"` | Registry key via `panel.id` |
| `.path(...)` | `/{id}` | Leading `/` is added if missing |
| `.brand_name(...)` | `"Orbit"` | Shown in the shell |
| `.brand_logo(...)` | `None` | Stored for your templates |
| `.font(...)` | `"Outfit"` | Shell typography |
| `.colors(**hex)` | `primary="#f1511b"` | Merges into the color map |

## Contents

| Method | What it stores |
|--------|----------------|
| `.resources([...])` | Resource classes (replaces the list) |
| `.pages([...])` | Custom page classes |
| `.widgets([...])` | Dashboard widgets |
| `.middleware([...])` | Defaults to `["auth", "permission"]` |
| `.login(True)` | Login enabled flag |
| `.auth_guard("web")` | Guard name |
| `.dark_mode()` / `.sidebar_collapsible()` | Shell preferences |
| `.plugin(callback)` | Stores a callback for later |

### Discovery paths

```python
panel.discover_resources("app/orbit/resources")
panel.discover_pages("app/orbit/pages")
panel.discover_widgets("app/orbit/widgets")
```

These append path strings onto the panel for tooling and future auto-import. **Today you still register classes** with `.resources([...])` (and friends). Treat discovery as a reserved hook, not magic yet.

## Registry

```python
registry = app.make(PanelRegistry)
registry.register(panel)
registry.get("admin")   # Panel | None
registry.all()          # list[Panel]
```

`OrbitServiceProvider` binds `PanelRegistry` as a singleton.

## Navigation

```python
items = panel.navigation_items()
# [{label, icon, group, subgroup, url, sort}, ...]
```

Items come from each resource and page’s navigation class vars, plus custom `NavigationItem`s, sorted by `navigation_sort`. Layouts: `sidebar`, `top`, `sidebar_topbar`. Full guide: [Navigation](/navigation/overview/).

Actions on the shell (modal vs URL, `mountAction`): [Panel actions](/panels/actions/).

## The shell

```python
html = panel.render_shell(content_html, user=request.user)
```

You get a full HTML document: sidebar, brand, and links to `/vendor/orbit/orbit.css` + `orbit.js`. Pass the authenticated user so permission-aware nav can filter itself.

## Multiple panels

Need a public “docs” panel and a private “admin” panel? Make two IDs, register both, and route to the one you want:

```python
Panel.make("admin").path("admin").resources([PostResource])
Panel.make("docs").path("docs").resources([ArticleResource]).login(False)
```

Next: [Resources](/resources/overview/).

## Preview

![Panel shell (light)](/examples/light/shell.png)

![Panel shell (dark)](/examples/dark/shell.png)
