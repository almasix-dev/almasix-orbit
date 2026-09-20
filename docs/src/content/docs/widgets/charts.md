---
title: Charts
description: ChartWidget with Chart.js (default) or ApexCharts via .chart_library — labels, datasets, filters, and empty states.
---

## Introduction

`ChartWidget` draws dashboard charts. **Chart.js** is the default library. Switch to **ApexCharts** with `.chart_library("apex")` or `.chart_library(ChartLibrary.APEX)`. The panel shell loads both vendor scripts; Alpine `orbitChart` picks the runtime from `data-chart-library`.

```python title="app/orbit/widgets/signups_chart.py"
from almasix.orbit.widgets import ChartWidget

ChartWidget.make("signups")
    .heading("Signups")
    .description("Last 7 days")
    .chart_type("line")
    .labels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    .datasets([{"label": "Users", "data": [12, 19, 14, 22, 18, 25, 30]}])
    .color("primary")
    .max_height("280px")
```

![Orbit Chart.js widget (light)](/examples/light/widgets/charts.png)

![Orbit Chart.js widget (dark)](/examples/dark/widgets/charts.png)

## Chart libraries

| Library | How to select | Payload |
|---------|---------------|---------|
| Chart.js (default) | `.chart_library("chartjs")` or omit | `get_data()` — `type` / `labels` / `datasets` / `options` |
| ApexCharts | `.chart_library("apex")` or `ChartLibrary.APEX` | `get_apex_options()` or `.apex_options({...})` |

```python title="app/orbit/widgets/chart_libraries.py"
from almasix.orbit.widgets import ChartLibrary, ChartWidget

# Chart.js (default)
ChartWidget.make("js")
    .heading("Chart.js")
    .chart_library(ChartLibrary.CHARTJS)
    .chart_type("bar")
    .labels(["A", "B", "C"])
    .datasets([{"label": "Series", "data": [3, 7, 4]}])

# ApexCharts
ChartWidget.make("apex")
    .heading("ApexCharts")
    .chart_library(ChartLibrary.APEX)
    .chart_type("area")
    .labels(["A", "B", "C"])
    .datasets([{"label": "Series", "data": [3, 7, 4]}])
```

![Orbit Chart libraries (light)](/examples/light/widgets/charts/libraries.png)

![Orbit Chart libraries (dark)](/examples/dark/widgets/charts/libraries.png)

When using Apex without a custom `.apex_options(...)`, Orbit translates Chart.js-shaped labels/datasets into an Apex options object (doughnut → donut, pie/donut series flattening, x-axis categories).

## Chart type

`.chart_type(...)` accepts Chart.js types such as `line`, `bar`, `doughnut`, `pie`, and `radar`. Apex receives the same string (with doughnut remapped to donut).

```python title="app/orbit/widgets/chart_types.py"
from almasix.orbit.widgets import ChartWidget

ChartWidget.make("bars")
    .heading("By channel")
    .chart_type("bar")
    .labels(["Organic", "Ads", "Referral"])
    .datasets([{"label": "Visits", "data": [40, 28, 17]}])

ChartWidget.make("share")
    .heading("Share")
    .chart_type("doughnut")
    .labels(["Pro", "Free", "Trial"])
    .datasets([{"data": [55, 30, 15]}])
```

![Orbit Chart types (light)](/examples/light/widgets/charts/types.png)

![Orbit Chart types (dark)](/examples/dark/widgets/charts/types.png)

## Labels and datasets

`.labels([...])` and `.datasets([{...}])` mirror the Chart.js data model. Dataset keys such as `label`, `data`, `backgroundColor`, and `borderColor` pass through to Chart.js; Apex translation uses `label` + `data`.

```python title="app/orbit/widgets/chart_data.py"
from almasix.orbit.widgets import ChartWidget

ChartWidget.make("multi")
    .heading("Revenue vs costs")
    .chart_type("line")
    .labels(["Jan", "Feb", "Mar", "Apr"])
    .datasets([
        {"label": "Revenue", "data": [12, 19, 14, 22]},
        {"label": "Costs", "data": [8, 11, 9, 13]},
    ])
```

![Orbit Chart datasets (light)](/examples/light/widgets/charts/datasets.png)

![Orbit Chart datasets (dark)](/examples/dark/widgets/charts/datasets.png)

## Options

`.options({...})` merges into Chart.js `options`. For Apex, either rely on translation + shallow merge, or set a full Apex tree with `.apex_options({...})` (wins when present).

```python title="app/orbit/widgets/chart_options.py"
from almasix.orbit.widgets import ChartLibrary, ChartWidget

ChartWidget.make("tuned")
    .heading("Tuned Chart.js")
    .labels(["Q1", "Q2", "Q3"])
    .datasets([{"label": "N", "data": [1, 3, 2]}])
    .options({"plugins": {"legend": {"display": False}}})

ChartWidget.make("apex_raw")
    .heading("Raw Apex")
    .chart_library(ChartLibrary.APEX)
    .apex_options({
        "chart": {"type": "bar", "toolbar": {"show": False}},
        "series": [{"name": "N", "data": [1, 3, 2]}],
        "xaxis": {"categories": ["Q1", "Q2", "Q3"]},
    })
```

## Color and height

`.color("primary")` sets `or-color-*` on the chart host. `.max_height("300px")` caps the canvas container (default `300px`).

```python title="app/orbit/widgets/chart_chrome.py"
from almasix.orbit.widgets import ChartWidget

ChartWidget.make("compact")
    .heading("Compact")
    .color("success")
    .max_height("200px")
    .labels(["Mon", "Tue", "Wed"])
    .datasets([{"label": "Hits", "data": [4, 6, 5]}])
```

![Orbit Chart chrome (light)](/examples/light/widgets/charts/chrome.png)

![Orbit Chart chrome (dark)](/examples/dark/widgets/charts/chrome.png)

## Filters

`.filters({"7d": "7 days", "30d": "30 days"})` renders tab buttons above the chart. `.filter("7d")` marks the active key (decorative in static HTML; wire to your host for live swaps).

```python title="app/orbit/widgets/chart_filters.py"
from almasix.orbit.widgets import ChartWidget

ChartWidget.make("range")
    .heading("Traffic")
    .filters({"7d": "7 days", "30d": "30 days", "90d": "90 days"})
    .filter("7d")
    .labels(["Mon", "Tue", "Wed"])
    .datasets([{"label": "Views", "data": [10, 14, 12]}])
```

![Orbit Chart filters (light)](/examples/light/widgets/charts/filters.png)

![Orbit Chart filters (dark)](/examples/dark/widgets/charts/filters.png)

## Empty state

When labels and datasets are empty (and no Apex options), `.empty_state_heading` / `.empty_state_description` render a friendly placeholder instead of a blank canvas.

```python title="app/orbit/widgets/chart_empty.py"
from almasix.orbit.widgets import ChartWidget

ChartWidget.make("empty")
    .heading("Conversions")
    .empty_state_heading("No data yet")
    .empty_state_description("Publish a campaign to see conversion trends.")
```

![Orbit Chart empty state (light)](/examples/light/widgets/charts/empty.png)

![Orbit Chart empty state (dark)](/examples/dark/widgets/charts/empty.png)

## Collapsible

`.collapsible()` sets `data-collapsible="true"` for hosts that fold chart bodies.

## On the dashboard

Subclass `ChartWidget`, set `sort` / `column_span`, configure data in `__init__`, and register with `Panel.widgets([...])`. Prefer Chart.js for lightweight sparklines-adjacent dashboards; choose Apex when you need its chart types or option surface.
