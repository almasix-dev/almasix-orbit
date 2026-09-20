---
title: Delete action
description: DeleteAction and DeleteBulkAction — danger confirmations for removing records.
---

## Introduction

`DeleteAction` permanently removes a record after confirmation. Defaults: name `delete`, label **Delete**, trash icon, danger color, confirmation on.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import DeleteAction

DeleteAction.make()
    .action(lambda record, **_: delete_post(record))
```

![Orbit DeleteAction (light)](/examples/light/actions/delete.png)

![Orbit DeleteAction (dark)](/examples/dark/actions/delete.png)

Default modal copy:

- Heading: **Delete?**
- Description: **This permanently removes the record.**

Override with `.modal_heading` / `.modal_description` / `.modal_submit_action_label`.

## Without confirmation

Only when you truly need an immediate delete (rare):

```python title="app/orbit/actions/delete_no_confirm.py"
from almasix.orbit.actions import DeleteAction

DeleteAction.make().without_confirmation()
```

Danger actions otherwise always confirm — Conduit-safe.

## Bulk delete

`DeleteBulkAction` targets the selected set. Defaults: name `delete_bulk`, label **Delete selected**, same danger + confirmation pattern.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import DeleteBulkAction

table.bulk_actions([
    DeleteBulkAction.make()
        .chunk_selected_records(100)
        .authorize_individual_records()
        .action(lambda records, **_: delete_many(records)),
])
```

Bulk helpers on `BulkAction`:

| Method | Role |
|--------|------|
| `.chunk_selected_records` | Process in batches |
| `.fetch_selected_records` | Host should hydrate models (default `True`) |
| `.authorize_individual_records` | Per-row authorize before delete |

## Lifecycle

```python title="app/orbit/actions/delete_lifecycle.py"
from almasix.orbit.actions import DeleteAction

DeleteAction.make()
    .before(lambda record, action, **_: action.halt() if record.get("locked") else None)
    .using(lambda record, **_: hard_delete(record))
    .after(lambda record, **_: log_audit("deleted", record))
    .success_notification("Deleted")
```
