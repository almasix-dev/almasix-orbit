---
title: Dashboard
description: Panel home page — widget grid, columns, filters, and multi-dashboard route paths.
---

## Introduction

The **Dashboard** is the default first page for a panel (home route `/` under the panel path). It lays out registered [widgets](/widgets/overview/) in a responsive CSS grid and optionally renders a filters form above the cards.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel
from app.orbit.app.widgets import OverviewStats, SignupsChart, RevenueApex, RecentPosts

Panel.make("admin")
    .path("admin")
    .widgets([OverviewStats, SignupsChart, RevenueApex, RecentPosts])
```

![Orbit Dashboard (light)](/examples/light/panels/dashboard.png)

![Orbit Dashboard (dark)](/examples/dark/panels/dashboard.png)

With no widgets registered, the page shows a short welcome message using the panel brand name.

## Register widgets

Prefer `Panel.widgets([...])`. The default `Dashboard.get_widgets` returns `panel.get_widgets()`. Discovery via `discover_widgets` / `discover_panel_dirs` also appends `Widget` subclasses under `app/orbit/{panel}/widgets/`.

```python title="app/orbit/app/panel.py"
Panel.make("app")
    .widgets([OverviewStats, SignupsChart])
    .discover_panel_dirs()
```

![Orbit Dashboard widgets (light)](/examples/light/panels/dashboard/widgets.png)

![Orbit Dashboard widgets (dark)](/examples/dark/panels/dashboard/widgets.png)

## Columns

Override `get_columns` to set the grid. Return an `int` or a breakpoint map (`default` / `sm` / `md` / `lg` / `xl`).

```python title="app/orbit/pages/dashboard.py"
from almasix.orbit.panels.pages import Dashboard

class AdminDashboard(Dashboard):
    @classmethod
    def get_columns(cls) -> int | dict[str, int]:
        return {"default": 1, "md": 2, "xl": 3}
```

![Orbit Dashboard columns (light)](/examples/light/panels/dashboard/columns.png)

![Orbit Dashboard columns (dark)](/examples/dark/panels/dashboard/columns.png)

The page emits `--or-dashboard-cols` (and breakpoint custom properties) on `.or-dashboard-widgets`.

## Custom widget list

Override `get_widgets` when a dashboard should not use the panel-wide list — useful for analytics-only pages.

```python title="app/orbit/pages/analytics_dashboard.py"
from almasix.orbit.panels.pages import Dashboard
from app.orbit.app.widgets import RevenueApex, SignupsChart

class AnalyticsDashboard(Dashboard):
    title = "Analytics"

    @classmethod
    def get_widgets(cls, panel=None):
        return [SignupsChart, RevenueApex]
```

## Filters form

`Dashboard.filters_form(schema)` stores a form/schema rendered above the widget grid. Filter state is passed to widgets as `page_filters` (widgets can call `filter_value("key")`).

```python title="app/orbit/pages/filtered_dashboard.py"
from almasix.orbit.forms import Select
from almasix.orbit.panels.pages import Dashboard

class FilteredDashboard(Dashboard):
    persists_filters_in_session = True

FilteredDashboard.filters_form(
    Select.make("range")
    .label("Range")
    .options({"7d": "7 days", "30d": "30 days"})
)
```

![Orbit Dashboard filters (light)](/examples/light/panels/dashboard/filters.png)

![Orbit Dashboard filters (dark)](/examples/dark/panels/dashboard/filters.png)

Set `persists_filters_in_session = True` to keep values across requests. Optional `header_filter_actions([...])` (and `filters_in_header`) place FilterAction-like controls beside the page title.

## Multi-dashboard route path

Subclass `Dashboard`, set `route_path` (e.g. `"analytics"`), and register the page on the panel. The default home dashboard stays at `/`; additional dashboards mount under their path segment.

```python title="app/orbit/pages/analytics_dashboard.py"
from almasix.orbit.panels.pages import Dashboard

class AnalyticsDashboard(Dashboard):
    title = "Analytics"
    route_path = "analytics"
    navigation_label = "Analytics"
    navigation_icon = "heroicon-o-chart-bar"
    navigation_sort = -90

    @classmethod
    def get_columns(cls) -> int:
        return 2
```

```python title="app/providers/orbit_panel_provider.py"
Panel.make("admin")
    .pages([AnalyticsDashboard])
    .widgets([...])  # home dashboard
```

![Orbit multi-dashboard (light)](/examples/light/panels/dashboard/route-path.png)

![Orbit multi-dashboard (dark)](/examples/dark/panels/dashboard/route-path.png)

`get_route_path()` exposes the class attribute for routing helpers.

## Replace the default dashboard

```python title="app/providers/orbit_panel_provider.py"
Panel.make("admin")
    .dashboard(AdminDashboard)  # or .dashboard(False) to disable
```

When the dashboard is disabled and resources exist, the first resource list becomes home.

## Rendering contract

`Dashboard.render(**ctx)` resolves widgets, sorts by `.get_sort()`, skips `can_view` failures, and joins HTML into the grid. Pass `page_filters`, `columns`, or `widgets` in `ctx` to override class defaults (handy in tests and gallery shots).
