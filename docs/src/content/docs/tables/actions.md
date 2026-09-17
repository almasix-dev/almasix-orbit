---
title: Table actions
description: Row, bulk, and header actions — ⋮ dropdowns, danger confirms, and ActionGroup.
---

Actions let a table open a page, confirm a delete, or run a callback without leaving the index. Three slots use the same Action objects as the rest of Orbit.

```python
from almasix.orbit.tables import Table, TextColumn
from almasix.orbit.actions import (
    Action, ActionGroup, CreateAction, EditAction, DeleteAction, DeleteBulkAction,
)

table = (
    Table.make("posts")
    .columns([TextColumn.make("title").searchable()])
    .header_actions([CreateAction.make()])
    .actions([
        EditAction.make(),
        ActionGroup.make([
            Action.make("archive")
                .label("Archive")
                .color("warning")
                .requires_confirmation(),
            DeleteAction.make(),
        ]),
    ])
    .bulk_actions([DeleteBulkAction.make()])
)
```

![Table actions (light)](/examples/light/tables/actions.png)
![Table actions (dark)](/examples/dark/tables/actions.png)

## Slots

| Slot | Method | When |
|------|--------|------|
| Header | `.header_actions([...])` | Create, export, and other list-level actions |
| Row | `.actions([...])` | View / Edit / Delete / custom per record |
| Bulk | `.bulk_actions([...])` | Operate on the selection |

```python
table.actions([...])         # per row
table.bulk_actions([...])    # selected rows
table.header_actions([...])  # top of the table
```

Crowded row actions collapse into a **⋮** dropdown (`ActionGroup`). Bulk actions can use `BulkActionGroup` when the host packs them.

## Danger confirms

Color `danger` means the action confirms first. Deletes confirm by default; other danger actions open the confirm dialog unless you call `.without_confirmation()`.

```python
from almasix.orbit.actions import Action, DeleteAction

DeleteAction.make()  # confirm modal by default

Action.make("purge")
    .label("Purge")
    .color("danger")
    .requires_confirmation()
    .modal_heading("Purge forever?")
    .modal_description("This cannot be undone.")
    .action(lambda record=None, **_: purge(record))
```

See [Panel actions](/panels/actions/) for modal vs page URL, `mountAction`, and Resource defaults (View / Edit / Delete / Create when slots are empty).

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, TextColumn
from almasix.orbit.actions import Action, ActionGroup, EditAction, DeleteAction

class PostResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return (
            table.columns([TextColumn.make("title").searchable()])
            .actions([
                EditAction.make(),
                ActionGroup.make([
                    Action.make("feature")
                        .label("Feature")
                        .action(lambda record=None, **_: feature(record)),
                    DeleteAction.make(),
                ]),
            ])
        )
```

Empty lists can still offer create:

```python
from almasix.orbit.actions import CreateAction

table.empty_state_actions([CreateAction.make()])
```

![Empty state actions (light)](/examples/light/tables/empty.png)
![Empty state actions (dark)](/examples/dark/tables/empty.png)

More presets: [Actions overview](/actions/overview/).
