---
title: Stats overview
description: Fluent Stat cards with icons, descriptions, colors, URLs, and Chart.js sparklines for Orbit dashboards.
---

## Introduction

`StatsOverviewWidget` renders a horizontal row of **stat cards** — compact KPI tiles that show a label, a primary value, and optional extras (description, icon, color, sparkline, or link).

Build each card with the fluent `Stat` API, then attach the list with `.stats([...])`. Register the widget on the panel like any other [widget](/widgets/overview/).

```python title="app/orbit/widgets/overview_stats.py"
from almasix.orbit.widgets import Stat, StatsOverviewWidget

StatsOverviewWidget.make("overview")
    .heading("Overview")
    .stats([
        Stat.make("Users")
            .value(1280)
            .description("+4% this week")
            .description_icon("heroicon-m-arrow-trending-up")
            .color("success")
            .icon("heroicon-o-users"),
        Stat.make("Posts").value(342).color("primary").icon("heroicon-o-document-text"),
        Stat.make("Revenue").value("$12.4k").color("warning").icon("heroicon-o-banknotes"),
    ])
```

![Orbit Stats overview (light)](/examples/light/widgets/stats-overview.png)

![Orbit Stats overview (dark)](/examples/dark/widgets/stats-overview.png)

Markup is `<div class="or-stats">` wrapping each `.or-stat`. Import `Stat` from `almasix.orbit.widgets` (same package as the widget).

## Value and placeholder

`.value(...)` sets the primary figure. When the value is missing, `.placeholder(...)` shows fallback copy instead of a blank card.

```python title="app/orbit/widgets/stat_value.py"
from almasix.orbit.widgets import Stat

Stat.make("Open tickets").value(12)
Stat.make("Queued jobs").placeholder("—")
```

![Orbit Stat value (light)](/examples/light/widgets/stats-overview/value.png)

![Orbit Stat value (dark)](/examples/dark/widgets/stats-overview/value.png)

## Description and icon

`.description(...)` adds a secondary line. `.description_icon(...)` prefixes that line with a small Heroicon. `.icon(...)` places a larger icon beside the copy.

```python title="app/orbit/widgets/stat_description.py"
from almasix.orbit.widgets import Stat

Stat.make("Signups")
    .value(86)
    .description("vs last week")
    .description_icon("heroicon-m-arrow-trending-up")
    .icon("heroicon-o-user-plus")
    .color("success")
```

![Orbit Stat description (light)](/examples/light/widgets/stats-overview/description.png)

![Orbit Stat description (dark)](/examples/dark/widgets/stats-overview/description.png)

## Color

`.color(...)` maps to `or-color-{name}` (primary, success, warning, danger, info, gray, …).

```python title="app/orbit/widgets/stat_colors.py"
from almasix.orbit.widgets import Stat

Stat.make("Healthy").value("OK").color("success")
Stat.make("Attention").value(3).color("warning")
Stat.make("Failed").value(1).color("danger")
```

![Orbit Stat colors (light)](/examples/light/widgets/stats-overview/colors.png)

![Orbit Stat colors (dark)](/examples/dark/widgets/stats-overview/colors.png)

## Sparklines

`.chart([3, 5, 4, 8, 7])` embeds a mini Chart.js sparkline via Alpine `orbitSparkline`. Values are numeric; color follows the stat’s `.color(...)`.

```python title="app/orbit/widgets/stat_chart.py"
from almasix.orbit.widgets import Stat, StatsOverviewWidget

StatsOverviewWidget.make("trends").stats([
    Stat.make("Users")
        .value(1280)
        .color("success")
        .chart([820, 932, 901, 1034, 1190, 1280]),
    Stat.make("Sessions")
        .value("4.2k")
        .color("primary")
        .chart([2.1, 2.4, 2.8, 3.1, 3.6, 4.2]),
])
```

![Orbit Stat sparklines (light)](/examples/light/widgets/stats-overview/chart.png)

![Orbit Stat sparklines (dark)](/examples/dark/widgets/stats-overview/chart.png)

## URL

`.url(...)` wraps the card in an `<a class="or-stat">` so the whole card is clickable.

```python title="app/orbit/widgets/stat_url.py"
from almasix.orbit.widgets import Stat

Stat.make("Users")
    .value(1280)
    .url("/admin/users")
    .icon("heroicon-o-users")
    .color("primary")
```

![Orbit Stat URL (light)](/examples/light/widgets/stats-overview/url.png)

![Orbit Stat URL (dark)](/examples/dark/widgets/stats-overview/url.png)

## Dynamic stats

Pass callables in `.stats([...])` — they receive evaluated context and may return a `Stat` or a sequence of stats.

```python title="app/orbit/widgets/stat_dynamic.py"
from almasix.orbit.widgets import Stat, StatsOverviewWidget

def user_stat(**ctx):
    count = ctx.get("user_count", 0)
    return Stat.make("Users").value(count).color("success")

StatsOverviewWidget.make("live").stats([user_stat])
```

## On the dashboard

Subclass `StatsOverviewWidget`, set `sort` / `heading`, and configure stats in `__init__` (or override `get_stats`). Register the class on the panel with `.widgets([...])`.
