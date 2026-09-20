---
title: Export action
description: ExportAction — download CSV/JSON with formats, columns, filename, and host-owned Exporter adapters.
---

## Introduction

`ExportAction` downloads the current table / query as a file. Defaults: name `export`, label **Export**, arrow-down-tray icon, gray color.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ExportAction

ExportAction.make()
    .formats(["csv", "json"])
    .columns(["title", "status", "published_at"])
    .column_map({"title": "Title", "status": "Status"})
    .filename("posts-export")
    .chunk_size(500)
    .max_rows(50_000)
    .exporter(run_export)
```

![Orbit ExportAction (light)](/examples/light/actions/export.png)

![Orbit ExportAction (dark)](/examples/dark/actions/export.png)

## Configuration bag

| Method | Role |
|--------|------|
| `.formats` | Allowed formats (`data-formats`) |
| `.columns` | Attribute list to include |
| `.column_map` | Attribute → header label |
| `.filename` | Base name (string or callable) |
| `.chunk_size` / `.max_rows` | Streaming limits |
| `.exporter` | Callable / `Exporter` subclass |

## Adapter contract

Like import, the **host** owns the job. Subclass `Exporter` or pass a callable:

```python title="app/orbit/exporters/post_exporter.py"
from almasix.orbit.actions import Exporter

class PostExporter(Exporter):
    def __call__(self, records=None, **kwargs):
        # Stream records to CSV/JSON; return path or response
        return "/tmp/posts.csv"
```

```python title="app/orbit/actions/export_wire.py"
from almasix.orbit.actions import ExportAction

ExportAction.make().exporter(PostExporter())
# or
ExportAction.make().action(lambda records, **_: stream_csv(records))
```

`.call()` prefers `.using` / `.action`; otherwise invokes `.exporter`.

## Filename callables

```python title="app/orbit/actions/export_filename.py"
from almasix.orbit.actions import ExportAction
from datetime import date

ExportAction.make().filename(lambda **_: f"posts-{date.today().isoformat()}")
```

## Header placement

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ExportAction, ImportAction

table.header_actions([
    ImportAction.make().importer(PostImporter()),
    ExportAction.make().exporter(PostExporter()),
])
```
