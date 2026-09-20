---
title: Import action
description: ImportAction uploads CSV or JSON, maps columns, and writes records through the in-process job runner.
---

## Introduction

`ImportAction` is the header button that brings records in. The operator opens a modal, supplies a CSV or JSON payload, and Orbit runs the job **in the same request**: parse → apply `.column_map()` → chunk → write rows onto the resource (or call your `.importer()`).

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ImportAction

table.header_actions([
    ImportAction.make()
        .accepted_file_types([".csv", ".json"])
        .column_map({"Title": "title", "Status": "status"})
        .chunk_size(100)
        .max_rows(10_000),
])
```

The list host listens for `mountAction("import", payload={...})`. Send `content` (the file body) and optional `filename`; the runner returns `{imported, failed, skipped, chunks, errors}` and dispatches `orbit-import-finished`.

![Orbit ImportAction (light)](/examples/light/actions/import.png)

![Orbit ImportAction (dark)](/examples/dark/actions/import.png)

## Configuration

| Method | Role |
|--------|------|
| `.accepted_file_types` | Extensions shown on the file input |
| `.options` | Extra dict merged into the job (e.g. `delimiter`) |
| `.options_form` | Extra modal fields |
| `.column_map` | CSV header → attribute |
| `.chunk_size` | Rows per write (default `500`) |
| `.max_rows` | Hard cap (`None` = unlimited) |
| `.importer` | Optional per-chunk callable |

Without an importer, the list host appends each mapped row to the resource’s records.

## Custom importer

When you need to hit an API or an ORM yourself, pass `.importer(...)`. It is called as `importer(path, options=..., rows=chunk)` for every chunk.

```python title="app/orbit/importers/post_importer.py"
from almasix.orbit.actions import Importer, ImportAction

class PostImporter(Importer):
    def __call__(self, path, *, options=None, rows=None, **kwargs):
        Post.insert(list(rows or []))

ImportAction.make().importer(PostImporter())
```

## Queueing

The default `ImmediateJobRunner` runs inside the request. Replace it to push the same `ImportAction` onto a queue:

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit.actions import set_job_runner

set_job_runner(CeleryJobRunner())
```

Your runner must implement `run_import(action, source, **kwargs)` and `run_export(action, records, **kwargs)`.

## On a table header

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ExportAction, ImportAction

table.header_actions([
    ImportAction.make().column_map({"Title": "title"}),
    ExportAction.make().filename("posts"),
])
```
