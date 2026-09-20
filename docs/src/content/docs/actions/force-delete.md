---
title: Force-delete action
description: ForceDeleteAction and ForceDeleteBulkAction — permanently remove soft-deleted records.
---

## Introduction

`ForceDeleteAction` permanently destroys a soft-deleted (or protected) record. Defaults: name `force_delete`, label **Force delete**, trash icon, danger color, confirmation on.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ForceDeleteAction

ForceDeleteAction.make().action(lambda record, **_: force_delete(record))
```

![Orbit ForceDeleteAction (light)](/examples/light/actions/force-delete.png)

![Orbit ForceDeleteAction (dark)](/examples/dark/actions/force-delete.png)

Default modal copy:

- Heading: **Force delete?**
- Description: **This permanently removes the record and cannot be undone.**

## Bulk force-delete

`ForceDeleteBulkAction` mirrors the single-record preset for selection sets.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ForceDeleteBulkAction

table.bulk_actions([
    ForceDeleteBulkAction.make().action(lambda records, **_: force_delete_many(records)),
])
```

## Soft-delete workflow

Typical trashed-table row actions:

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import RestoreAction, ForceDeleteAction

table.actions([
    RestoreAction.make(),
    ForceDeleteAction.make(),
])
```

See [Restore](/actions/restore/) for the counterpart and [Delete](/actions/delete/) for soft delete.
