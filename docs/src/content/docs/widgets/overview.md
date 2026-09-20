---
title: Overview
description: Dashboard widgets — cards you register on a panel home page for stats, charts, tables, and custom HTML.
---

## Introduction

**Widgets** are dashboard-sized cards on a panel home page. Each widget is a Python class (or fluent instance) that renders a self-contained block of UI — a KPI strip, a chart, an embedded table, or custom HTML.

Register widget classes on the panel with `.widgets([...])`. The default [Dashboard](/panels/dashboard/) collects them, checks who can see each one, sorts by `.sort(...)`, and lays them out in a responsive grid.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel
from almasix.orbit.widgets import StatsOverviewWidget, ChartWidget, TableWidget

Panel.make("admin")
    .path("admin")
    .widgets([StatsOverviewWidget, ChartWidget, TableWidget])
```

![Orbit Widgets overview (light)](/examples/light/widgets/overview.png)

![Orbit Widgets overview (dark)](/examples/dark/widgets/overview.png)

Each widget renders a `<section class="or-widget">` with an optional header and body. Interactive charts boot through Alpine (`orbitChart` / `orbitSparkline`) with Chart.js or ApexCharts loaded by the panel shell.

## Widget types

| Widget | Role |
|--------|------|
| [Stats overview](/widgets/stats-overview/) | Row of fluent `Stat` cards (optional sparklines) |
| [Charts](/widgets/charts/) | Line / bar / doughnut charts via Chart.js or ApexCharts |
| [Tables](/widgets/tables/) | Embed a configured `Table` on the dashboard |
| Custom `Widget` | Override `render_body` for bespoke HTML |

```python title="app/orbit/widgets/examples.py"
from almasix.orbit.widgets import (
    ChartWidget,
    Stat,
    StatsOverviewWidget,
    TableWidget,
    Widget,
)
from almasix.orbit.tables import Table, TextColumn

StatsOverviewWidget.make("overview").stats([
    Stat.make("Users").value(1280).color("success").icon("heroicon-o-users"),
    Stat.make("Posts").value(342).color("primary"),
])

ChartWidget.make("signups")
    .heading("Signups")
    .chart_type("bar")
    .labels(["Mon", "Tue", "Wed"])
    .datasets([{"label": "Users", "data": [3, 7, 4]}])

TableWidget.make("recent").table(
    Table.make().columns([TextColumn.make("title")]).records(recent_posts)
)
```

## Heading and description

`.heading(...)` and `.description(...)` set the widget chrome above the body. Class attributes `heading` / `description` work the same via `__init_subclass__`.

```python title="app/orbit/widgets/heading.py"
from almasix.orbit.widgets import Widget

Widget.make("notes")
    .heading("Release notes")
    .description("Latest shipping updates for the team.")
```

![Orbit Widget heading (light)](/examples/light/widgets/overview/heading.png)

![Orbit Widget heading (dark)](/examples/dark/widgets/overview/heading.png)

## Sort order

Widgets are sorted ascending by `.sort(...)` (or class attribute `sort`) before render. Lower numbers appear first.

```python title="app/orbit/widgets/sort.py"
from almasix.orbit.widgets import StatsOverviewWidget, ChartWidget

class OverviewStats(StatsOverviewWidget):
    sort = 1

class SignupsChart(ChartWidget):
    sort = 10
```

![Orbit Widget sort (light)](/examples/light/widgets/overview/sort.png)

![Orbit Widget sort (dark)](/examples/dark/widgets/overview/sort.png)

## Column span

`.column_span(2)`, `.column_span("full")`, or `.column_span_full()` control grid placement. Pass a breakpoint map for responsive spans:

```python title="app/orbit/widgets/span.py"
from almasix.orbit.widgets import ChartWidget

ChartWidget.make("wide")
    .heading("Traffic")
    .column_span("full")

ChartWidget.make("responsive")
    .heading("By device")
    .column_span({"md": 1, "lg": 2})
```

![Orbit Widget column span (light)](/examples/light/widgets/overview/column-span.png)

![Orbit Widget column span (dark)](/examples/dark/widgets/overview/column-span.png)

## Polling

`.polling_interval(15)` (or `"15s"`) emits `data-polling` for the host to refresh the widget on an interval.

```python title="app/orbit/widgets/polling.py"
from almasix.orbit.widgets import StatsOverviewWidget

StatsOverviewWidget.make("live")
    .heading("Live metrics")
    .polling_interval(15)
```

## Lazy loading

`.lazy()` marks the widget with `data-lazy="true"` and a placeholder so the shell can defer heavy bodies until visible.

```python title="app/orbit/widgets/lazy.py"
from almasix.orbit.widgets import ChartWidget

ChartWidget.make("deferred")
    .heading("Heavy chart")
    .lazy()
```

## Visibility

Override classmethod `can_view(**ctx)` or chain `.can_view_when(...)` on an instance. Unauthorized widgets are omitted from the grid.

```python title="app/orbit/widgets/visibility.py"
from almasix.orbit.widgets import Widget

class AdminOnly(Widget):
    @classmethod
    def can_view(cls, **ctx) -> bool:
        user = ctx.get("user")
        return bool(user and getattr(user, "is_admin", False))

Widget.make("beta").can_view_when(lambda **ctx: ctx.get("feature_beta") is True)
```

![Orbit Widget visibility (light)](/examples/light/widgets/overview/visibility.png)

![Orbit Widget visibility (dark)](/examples/dark/widgets/overview/visibility.png)

## Custom widgets

Subclass `Widget` and implement `render_body`. Use `page_filters` / `filter_value` when the dashboard passes filter state.

```python title="app/orbit/widgets/welcome_widget.py"
from almasix.orbit.widgets import Widget
from almasix.orbit.support.html import e

class WelcomeWidget(Widget):
    sort = 0
    heading = "Welcome"

    def render_body(self, state=None, **ctx) -> str:
        brand = e(str(ctx.get("brand") or "Orbit"))
        return f'<p class="or-muted">Hello from {brand}.</p>'
```

![Orbit custom widget (light)](/examples/light/widgets/overview/custom.png)

![Orbit custom widget (dark)](/examples/dark/widgets/overview/custom.png)

## On a panel

```python title="app/providers/orbit_panel_provider.py"
Panel.make("admin")
    .widgets([OverviewStats, SignupsChart, RecentPosts, WelcomeWidget])
```

The default dashboard calls `panel.get_widgets()`. Override `Dashboard.get_widgets` for a page-specific set, or pass `widgets=[...]` into `Dashboard.render` for tests and custom pages. See [Dashboard](/panels/dashboard/).
