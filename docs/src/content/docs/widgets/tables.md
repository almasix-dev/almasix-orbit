---
title: Tables
description: Embed an Orbit Table on the dashboard with TableWidget.
---

## Introduction

`TableWidget` wraps a configured [`Table`](/tables/overview/) so recent records, queues, or mini indexes can sit beside stats and charts on the [Dashboard](/panels/dashboard/).

```python title="app/orbit/widgets/recent_posts.py"
from almasix.orbit.tables import Table, TextColumn, BadgeColumn
from almasix.orbit.widgets import TableWidget

TableWidget.make("recent_posts")
    .heading("Recent posts")
    .description("Latest five drafts and publications")
    .column_span("full")
    .table(
        Table.make()
        .columns([
            TextColumn.make("title").label("Title"),
            BadgeColumn.make("status").label("Status"),
        ])
        .records([
            {"title": "Launch Orbit", "status": "published"},
            {"title": "Conduit hosts", "status": "draft"},
        ])
        .paginated(False)
    )
```

![Orbit Table widget (light)](/examples/light/widgets/tables.png)

![Orbit Table widget (dark)](/examples/dark/widgets/tables.png)

The widget body is the table’s own `render()` output — same chrome as resource list tables (columns, empty state, optional actions).

## Configure the table

Build the table with the usual fluent API, then pass it to `.table(...)`. Call `.get_table()` when you need the instance later.

```python title="app/orbit/widgets/table_config.py"
from almasix.orbit.tables import Table, TextColumn
from almasix.orbit.widgets import TableWidget

widget = (
    TableWidget.make("queue")
    .heading("Job queue")
    .table(
        Table.make()
        .heading("Pending jobs")
        .columns([
            TextColumn.make("name"),
            TextColumn.make("attempts"),
        ])
        .records(pending_jobs)
        .paginated(False)
    )
)

assert widget.get_table() is not None
```

![Orbit Table widget config (light)](/examples/light/widgets/tables/basic.png)

![Orbit Table widget config (dark)](/examples/dark/widgets/tables/basic.png)

## Layout on the dashboard

Use base widget layout helpers so tables don’t squeeze beside narrow charts:

```python title="app/orbit/widgets/table_span.py"
from almasix.orbit.widgets import TableWidget

TableWidget.make("full_width")
    .heading("Activity")
    .column_span_full()
    .table(activity_table)
```

![Orbit Table widget full span (light)](/examples/light/widgets/tables/full-span.png)

![Orbit Table widget full span (dark)](/examples/dark/widgets/tables/full-span.png)

## Empty table

An unset table renders an empty body. Prefer configuring columns + records (even an empty list) so the table empty state can show:

```python title="app/orbit/widgets/table_empty.py"
from almasix.orbit.tables import Table, TextColumn
from almasix.orbit.widgets import TableWidget

TableWidget.make("empty")
    .heading("Mentions")
    .table(
        Table.make()
        .columns([TextColumn.make("author"), TextColumn.make("body")])
        .records([])
        .paginated(False)
    )
```

![Orbit Table widget empty (light)](/examples/light/widgets/tables/empty.png)

![Orbit Table widget empty (dark)](/examples/dark/widgets/tables/empty.png)

## On the dashboard

Subclass `TableWidget`, build the table in `__init__` (or a helper), set `sort`, and register the class on the panel. Keep dashboard tables small — disable pagination or limit records so the home page stays scannable.
