---
title: Relation managers
description: Show and manage related records — comments on a post, items on an order — right on a resource’s view and edit pages.
---

A **relation manager** is a table of records that belong to the record you are looking at: comments on a post, line items on an order, members of a team. You declare it once, attach it to the owning [resource](/resources/overview/), and Orbit renders it underneath the infolist on the view page and underneath the form on the edit page.

![Orbit relation manager (light)](/examples/light/resources/relation-manager.png)

![Orbit relation manager (dark)](/examples/dark/resources/relation-manager.png)

## Write one

Subclass `RelationManager`, name the relationship, and configure the table (and, if the rows are editable, a form):

```python title="app/orbit/relations/comments_relation_manager.py"
from almasix.orbit import RelationManager
from almasix.orbit.forms import Form, Select, TextInput, Textarea
from almasix.orbit.tables import BadgeColumn, Table, TextColumn

from app.models.comment import Comment


class CommentsRelationManager(RelationManager):
    relationship = "comments"
    title = "Comments"
    description = "Reader replies attached to this post."
    record_title_attribute = "author"
    related_model = Comment
    foreign_key = "post_id"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            TextInput.make("author").required().max_length(80),
            Textarea.make("body").rows(3).required(),
            Select.make("status").options({"visible": "Visible", "hidden": "Hidden"}),
        ])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("author").searchable().sortable(),
            TextColumn.make("body").limit(60).wrap(),
            BadgeColumn.make("status").colors({"visible": "success", "hidden": "gray"}),
        ])
```

Attach it to the resource that owns the records:

```python title="app/orbit/resources/post_resource.py"
class PostResource(Resource):
    model = Post

    @classmethod
    def get_relations(cls) -> list[type]:
        return [CommentsRelationManager]
```

That is the whole wiring step. The view and edit pages pick the managers up from `get_relations()`; you do not render them by hand.

## Where the rows come from

Orbit resolves related records in one of two ways:

| Setup | How rows load |
|-------|---------------|
| `related_model` is an ORM model | Queries `related_model.where(foreign_key, owner_id)` when the page mounts |
| No `related_model` | Reads `owner["comments"]` (dict records) or `owner.comments` (objects) |

`foreign_key` defaults to the owning resource's singular slug plus `_id` — a `PostResource` with slug `posts` looks for `post_id`. Set it explicitly when your column is named differently.

The second form is handy for demos and for records you already loaded: any list on the owner works, no database required.

## Configuration

| Class var | Role | Default |
|-----------|------|---------|
| `relationship` | Attribute / dict key holding the rows, and the manager's identity in action names | — |
| `title` | Heading above the table | Title-cased `relationship` |
| `description` | Sentence under the heading | `None` |
| `record_title_attribute` | How a related row introduces itself | `"id"` |
| `related_model` | ORM model to query | `None` |
| `foreign_key` | Column pointing back at the owner | `{owner}_id` |
| `render_on` | `"view"`, `"edit"`, or `"both"` | `"both"` |
| `is_mutable` | Adds create / delete chrome to the table | `True` |

Set `render_on = "edit"` for managers that only make sense while editing (revision history, internal notes), and `is_mutable = False` for read-only lists such as audit logs:

```python
class RevisionsRelationManager(RelationManager):
    relationship = "revisions"
    render_on = "edit"
    is_mutable = False
```

## Actions

A mutable manager renders a **New &lt;record&gt;** header action and a delete row action. Both are namespaced so the page host can route them back to the right manager:

```text
relation.comments.create
relation.comments.delete
```

Deleting a row removes it from the related model (ORM) or from the loaded rows (in-memory), and the page re-renders without a full reload. Every relation action also dispatches an `orbit-relation-action` browser event carrying the relationship, action, and record id, so custom JavaScript can react.

Supply your own actions when the defaults do not fit — anything you set in `table()` wins:

```python
@classmethod
def table(cls, table: Table) -> Table:
    return table.columns([...]).actions([
        Action.make("approve").icon("heroicon-o-check").color("success"),
    ])
```

## Authorization

```python
class CommentsRelationManager(RelationManager):
    @classmethod
    def can_view_for_record(cls, user, owner) -> bool:
        return user.can("posts.moderate", owner)
```

The page calls `can_view_for_record(user, owner)` for every manager before rendering it. With no signed-in user the manager renders (so panels work before you register policies); with a user, a `False` result hides the section entirely.

## Related pages

- [Resources overview](/resources/overview/) — the class that owns the managers
- [Viewing records](/resources/viewing-records/) and [Editing records](/resources/editing-records/) — the pages managers appear on
- [Tables](/tables/overview/) — every column, filter, and action available inside a manager
