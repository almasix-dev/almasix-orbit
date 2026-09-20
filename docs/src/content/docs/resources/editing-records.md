---
title: Editing records
description: The edit page — hydrating the form from a record, saving changes, header actions, and relation managers.
---

The edit page lives at `{resource}/{id}/edit`. It loads the record, fills the resource [form](/forms/overview/) with its values, and titles the page with the record itself — **Edit Launch Orbit** rather than *Edit Posts*.

## Loading the record

When the page mounts, Orbit finds the record by id — through the ORM model for database-backed resources, or from the resource's seed list — and hydrates the form field by field. Nested keys the schema does not cover (wizard bags, JSON columns) are kept in state so they survive a save.

The heading comes from `record_title_attribute`:

```python
class PostResource(Resource):
    record_title_attribute = "title"     # heading + breadcrumb leaf
```

Override `get_record_title(record)` for a computed title:

```python
@classmethod
def get_record_title(cls, record) -> str:
    return f"{record['reference']} — {record['customer']}"
```

The breadcrumb trail shows the same title and links it to the record's view page.

## Saving

Submitting the form validates the schema, writes the changes (ORM update or in-memory replace), dispatches `orbit-record-saved`, and redirects to the record's view page. A resource whose records are not mutable renders a read-only copy of the form with a short explanation instead.

## Header actions

The edit page shows View and Delete buttons by default. They are permission-aware: with a signed-in user, `can_view` and `can_delete` decide whether each appears; before you register policies everything stays visible so a fresh panel is usable.

## Relation managers

Every [relation manager](/resources/managing-relationships/) with `render_on` set to `"edit"` or `"both"` renders below the form, so a post's comments can be managed while the post itself is being edited:

```python
class PostResource(Resource):
    @classmethod
    def get_relations(cls) -> list[type]:
        return [CommentsRelationManager]
```

## Soft deletes

Turn on `soft_deletes` and the resource's table gains a trashed filter plus restore and force-delete actions, and the page hosts learn the `restore` action:

```python
class PostResource(Resource):
    soft_deletes = True
```

![Orbit soft-deleted records with restore actions (light)](/examples/light/resources/soft-deletes.png)

![Orbit soft-deleted records with restore actions (dark)](/examples/dark/resources/soft-deletes.png)

Restoring calls the model's `restore()` when it has one, and otherwise clears `deleted_at`.

## Related pages

- [Creating records](/resources/creating-records/) — the same schema before the record exists
- [Viewing records](/resources/viewing-records/) — the read-only counterpart
- [Relation managers](/resources/managing-relationships/) — nested tables on this page
