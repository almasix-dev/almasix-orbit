---
title: Relation managers
description: Nested CRUD for related records on a resource’s view/edit screens.
---

A **relation manager** is a mini resource scoped to a relationship — comments on a post, items on an order, that kind of thing.

```python
from almasix.orbit import RelationManager
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn


class CommentsRelationManager(RelationManager):
    relationship = "comments"
    title = "Comments"
    record_title_attribute = "body"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            TextInput.make("body").required(),
        ])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("body").limit(80),
            TextColumn.make("created_at").sortable(),
        ])
```

## Class vars

| Var | Role |
|-----|------|
| `relationship` | Name of the relation on the owner model |
| `title` | Heading in the UI |
| `record_title_attribute` | How related rows introduce themselves |

## Hooks

Same shape as resources:

```python
RelationManager.get_form()   # Form.make(f"{relationship}_form") then form()
RelationManager.get_table()  # Table.make(f"{relationship}_table") then table()
```

## Access

```python
CommentsRelationManager.can_view_for_record(user, owner)
# default: True when user is not None
```

Override when related data needs tighter gates than the parent resource.

## Wiring

```python
class PostResource(Resource):
    @classmethod
    def get_relations(cls) -> list[type]:
        return [CommentsRelationManager]
```

Your view/edit pages decide *where* to render the manager; the manager owns the form/table config.
