---
title: Pages
description: Custom panel pages that aren’t tied to a single resource’s CRUD cycle.
---

Not everything is a resource. **Pages** are free-standing destinations in the panel nav — dashboards, reports, settings screens, whatever doesn’t fit CRUD.

```python
from almasix.orbit import Page


class DashboardPage(Page):
    title = "Dashboard"
    navigation_label = "Dashboard"
    navigation_icon = "heroicon-o-home"
    navigation_group = None
    navigation_sort = -10
    slug = "dashboard"          # optional — derived from class name
    permission = "dashboard.view"

    @classmethod
    def render(cls, **ctx) -> str:
        return "<h1>Welcome back</h1>"
```

## Class vars

| Var | Default | Role |
|-----|---------|------|
| `title` | from label | Page heading |
| `navigation_label` | from slug | Sidebar text |
| `navigation_icon` | — | Heroicon name |
| `navigation_group` | `None` | Sidebar group |
| `navigation_sort` | `0` | Lower sorts first |
| `slug` | from class name | Strips a trailing `Page` → snake |
| `permission` | `None` | Gate for `can_access` |

## Access

```python
DashboardPage.can_access(user)  # True if no permission, or user passes the check
```

When `permission` is set, Orbit reuses the same ability resolution as resources. With no permission, any authenticated user (non-`None`) can access.

## Registering

```python
Panel.make("admin").pages([DashboardPage, SettingsPage])
```

Pages show up in `panel.navigation_items()` alongside resources.

## Rendering

The default `render()` is a thin title shell — override it and return HTML (or a Prism view string your app resolves). Drop widgets, stats, or a custom Conduit component inside; Orbit doesn’t mind.

```python
@classmethod
def render(cls, **ctx) -> str:
    stats = StatsOverviewWidget.make().stats([...]).render()
    return f"<div class='or-page'>{stats}</div>"
```

See also: [Widgets](/widgets/overview/), [Panels](/panels/configuration/).
