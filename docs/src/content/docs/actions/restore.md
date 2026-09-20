---
title: Restore action
description: RestoreAction and RestoreBulkAction — bring soft-deleted records back.
---

## Introduction

`RestoreAction` undeletes a soft-deleted record. Defaults: name `restore`, label **Restore**, check icon, success color, confirmation on.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import RestoreAction

RestoreAction.make().action(lambda record, **_: restore(record))
```

![Orbit RestoreAction (light)](/examples/light/actions/restore.png)

![Orbit RestoreAction (dark)](/examples/dark/actions/restore.png)

Default modal copy:

- Heading: **Restore?**
- Description: **Restore this soft-deleted record.**

## Bulk restore

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import RestoreBulkAction

table.bulk_actions([
    RestoreBulkAction.make().action(lambda records, **_: restore_many(records)),
])
```

![Orbit RestoreBulkAction (light)](/examples/light/actions/restore/bulk.png)

![Orbit RestoreBulkAction (dark)](/examples/dark/actions/restore/bulk.png)

## With TrashedFilter

Pair with table trash filters so restore only appears on deleted rows:

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import RestoreAction, ForceDeleteAction, DeleteAction
from almasix.orbit.tables.filters import TrashedFilter

table.filters([TrashedFilter.make()]).actions([
    DeleteAction.make().visible(lambda record, **_: not record.get("deleted_at")),
    RestoreAction.make().visible(lambda record, **_: bool(record.get("deleted_at"))),
    ForceDeleteAction.make().visible(lambda record, **_: bool(record.get("deleted_at"))),
])
```
