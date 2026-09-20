---
title: Import action
description: ImportAction — upload CSV/JSON with options form, column map, and host-owned Importer adapters.
---

## Introduction

`ImportAction` opens a modal for uploading records. Defaults: name `import`, label **Import**, arrow-up-tray icon, gray color, modal on.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ImportAction
from almasix.orbit.forms import TextInput

ImportAction.make()
    .accepted_file_types([".csv", ".json"])
    .options_form([TextInput.make("delimiter").label("Delimiter").default(",")])
    .column_map({"Title": "title", "Status": "status"})
    .chunk_size(500)
    .max_rows(10_000)
    .importer(run_import)
```

![Orbit ImportAction (light)](/examples/light/actions/import.png)

![Orbit ImportAction (dark)](/examples/dark/actions/import.png)

## Configuration bag

| Method | Role |
|--------|------|
| `.accepted_file_types` | Extensions / MIME hints (`data-accept`) |
| `.options` | Opaque dict merged into job options |
| `.options_form` | Extra modal fields (also merged into `.form`) |
| `.column_map` | Header → attribute mapping |
| `.chunk_size` | Rows per chunk (default `500`) |
| `.max_rows` | Hard cap (`None` = unlimited) |
| `.importer` | Callable / `Importer` subclass |

## Adapter contract

Orbit does **not** run a job queue. The panel host uploads the file, reads `to_dict()` config, and invokes your importer.

```python title="app/orbit/importers/post_importer.py"
from almasix.orbit.actions import Importer

class PostImporter(Importer):
    def __call__(self, path: str, *, options=None, **kwargs):
        # Parse CSV/JSON at path; honor options["delimiter"], column_map, chunks…
        return imported_count
```

Wire either a subclass instance or any callable:

```python title="app/orbit/actions/import_wire.py"
from almasix.orbit.actions import ImportAction

ImportAction.make().importer(PostImporter())
# or
ImportAction.make().action(lambda path, **_: custom_import(path))
```

`.call()` prefers `.using` / `.action` when set; otherwise calls `.importer`.

## On a table header

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ExportAction, ImportAction

table.header_actions([
    ImportAction.make().importer(PostImporter()),
    ExportAction.make().exporter(PostExporter()),
])
```
