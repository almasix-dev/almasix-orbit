---
title: Widgets
description: Dashboard widgets — stats overviews, charts, and embedded tables.
---

Widgets are dashboard-sized building blocks. Drop them on a [Page](/navigation/custom-pages/) or anywhere you render Orbit HTML.

```python
from almasix.orbit.widgets import (
    StatsOverviewWidget, ChartWidget, TableWidget, Widget,
)
from almasix.orbit.widgets.widget import Stat
from almasix.orbit.tables import Table, TextColumn

stats = StatsOverviewWidget.make("overview").stats([
    Stat(
        label="Users",
        value=1280,
        description="+4% this week",
        color="success",
        icon="heroicon-o-users",
    ),
    Stat(label="Posts", value=342, color="primary"),
])

chart = (
    ChartWidget.make("signups")
    .heading("Signups")
    .chart_type("bar")
    .labels(["Mon", "Tue", "Wed"])
    .datasets([{"label": "Users", "data": [3, 7, 4]}])
)

table_widget = TableWidget.make("recent").table(
    Table.make().columns([TextColumn.make("title")]).records(recent_posts)
)
```

## Base widget

```python
Widget.make("w")
    .heading("Heading")
    .description("Optional blurb")
    .column_span_full()
```

`WidgetConfiguration(columns=2, polling=None)` is a small dataclass helper if you want to pass layout hints around.

## Types

| Widget | Role |
|--------|------|
| `StatsOverviewWidget` | Row of `Stat` cards |
| `ChartWidget` | Labels + datasets (you render/chart as needed) |
| `TableWidget` | Wraps a configured `Table` |

`Stat` lives at `almasix.orbit.widgets.widget.Stat` (not re-exported in `__all__` — import it from there).

## On a panel

```python
Panel.make("admin").widgets([StatsOverviewWidget, SignupsChart])
```

Widgets are stored on the panel for your dashboard page to pick up — wire them into `Page.render()` however you like.
