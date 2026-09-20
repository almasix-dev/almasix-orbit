---
title: Custom pages
description: Free-standing panel pages — navigation knobs, access gates, and registration.
---

## Introduction

Not everything is a resource. **Pages** are free-standing destinations in the panel nav — dashboards, reports, settings screens, anything that doesn’t fit CRUD.

```python title="app/orbit/pages/dashboard_page.py"
from almasix.orbit import Page

class DashboardPage(Page):
    title = "Dashboard"
    navigation_label = "Dashboard"
    navigation_icon = "heroicon-o-home"
    active_navigation_icon = "heroicon-s-home"
    navigation_group = None
    navigation_sort = -10
    slug = "dashboard"
    permission = "dashboard.view"

    @classmethod
    def render(cls, **ctx) -> str:
        return "<h1>Welcome back</h1>"
```

![Orbit custom pages (light)](/examples/light/navigation/custom-pages.png)

![Orbit custom pages (dark)](/examples/dark/navigation/custom-pages.png)

## Navigation class vars

Pages share the same navigation surface as resources:

| Var | Default | Role |
|-----|---------|------|
| `title` | from label | Page heading |
| `navigation_label` | from slug | Sidebar / topbar text |
| `navigation_icon` | `heroicon-o-home` | Heroicon name |
| `active_navigation_icon` | — | Icon when the item is active |
| `navigation_group` | `None` | Root group |
| `navigation_subgroup` / `navigation_sub_category` | — | Second-level category |
| `navigation_sort` | `0` | Lower sorts first |
| `navigation_badge` / `_color` / `_tooltip` | — | Badge chrome |
| `navigation_parent_item` | — | Nest under another item’s label |
| `should_register_navigation` | `True` | Omit from nav when `False` |
| `cluster` | — | Assign to a [cluster](/navigation/clusters/) |
| `slug` | from class name | Strips a trailing `Page` → snake |
| `permission` | `None` | Gate for `can_access` |

```python title="app/orbit/pages/reports_page.py"
class ReportsPage(Page):
    navigation_label = "Reports"
    navigation_icon = "heroicon-o-chart-bar"
    navigation_group = "Content"
    navigation_subgroup = "Insights"
    navigation_sort = 40
    navigation_badge = "Live"
    navigation_badge_color = "success"
```

## Access

```python title="app/orbit/pages/access.py"
DashboardPage.can_access(user)  # True if no permission, or user passes the check
```

When `permission` is set, Orbit reuses the same ability resolution as resources. With no permission, any authenticated user (non-`None`) can access. Pages that fail `can_access` are omitted from navigation when a user is present.

Override `get_should_register_navigation(**ctx)` for contextual hide (feature flags, tenancy, etc.) without removing the route.

## Registering

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel

Panel.make("admin")
    .path("admin")
    .pages([DashboardPage, SettingsPage])
```

Discovery via `.discover_pages(...)` / `.discover_panel_dirs()` also picks up `Page` subclasses under `app/orbit/{panel}/pages/`. Pages show up in `panel.navigation_items()` alongside resources.

## Rendering

The default `render()` is a thin title shell — override it and return HTML (or a Prism view string your app resolves). Drop widgets, stats, or a custom Conduit component inside.

```python title="app/orbit/pages/stats_page.py"
@classmethod
def render(cls, **ctx) -> str:
    stats = StatsOverviewWidget.make().stats([...]).render()
    return f"<div class='or-page'>{stats}</div>"
```

See also: [Navigation overview](/navigation/overview/), [Widgets](/widgets/overview/), [Panels](/panels/configuration/).
