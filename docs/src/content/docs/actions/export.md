---
title: Export action
description: ExportAction downloads the current table as CSV or JSON through the in-process job runner.
---

## Introduction

`ExportAction` is the header button that takes the current list of records (search, filters, and all) and turns it into a file. The default runner serialises CSV or JSON in the request and the browser downloads it from the `orbit-export-ready` event.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ExportAction

table.header_actions([
    ExportAction.make()
        .formats(["csv", "json"])
        .columns(["title", "status", "amount"])
        .column_map({"title": "Title", "status": "Status"})
        .filename("posts")
        .chunk_size(500)
        .max_rows(50_000),
])
```

`mountAction("export", payload={"format": "csv"})` returns `{filename, format, rows, content, mime}`.

![Orbit ExportAction (light)](/examples/light/actions/export.png)

![Orbit ExportAction (dark)](/examples/dark/actions/export.png)

## Configuration

| Method | Role |
|--------|------|
| `.formats` | Allowed formats (`csv`, `json`) |
| `.columns` | Attributes to include (all keys if omitted) |
| `.column_map` | Attribute → header label |
| `.filename` | Base name (string or callable) |
| `.chunk_size` / `.max_rows` | Limits for a custom exporter |
| `.exporter` | Optional callable that returns text, a dict, or an `ExportReport` |

## Custom exporter

```python title="app/orbit/exporters/post_exporter.py"
from almasix.orbit.actions import Exporter, ExportAction

class PostExporter(Exporter):
    def __call__(self, records=None, **kwargs):
        return {"content": render_xlsx(records), "filename": "posts.xlsx", "mime": "application/vnd.ms-excel"}

ExportAction.make().exporter(PostExporter()).formats(["xlsx"])
```

`.filename()` accepts a callable:

```python
from datetime import date
ExportAction.make().filename(lambda **_: f"posts-{date.today().isoformat()}")
```

## Queueing

Same runner as import — see [Import action](/actions/import/). `set_job_runner(...)` replaces both.

## Header placement

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ExportAction, ImportAction

table.header_actions([
    ImportAction.make().column_map({"Title": "title"}),
    ExportAction.make().filename("posts"),
])
```
