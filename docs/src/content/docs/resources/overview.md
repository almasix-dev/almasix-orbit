---
title: Overview
description: CRUD resources — forms, tables, infolists, permissions, and page routes.
---

A **resource** is one admin surface for a model: form, table, infolist, permissions, and the usual index / create / edit / view routes.

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn
from almasix.orbit.infolists import Infolist, TextEntry


class PostResource(Resource):
    model = Post
    slug = "posts"                       # optional — defaults to plural snake of the class
    navigation_label = "Posts"
    navigation_group = "Content"
    navigation_sort = 1
    navigation_icon = "heroicon-o-pencil-square"
    permission_prefix = "posts"          # optional — defaults to slug
    record_title_attribute = "title"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            TextInput.make("title").required(),
            TextInput.make("slug").required(),
        ])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("title").searchable().sortable(),
        ])

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist.schema([
            TextEntry.make("title"),
            TextEntry.make("slug").copyable(),
        ])

    @classmethod
    def get_relations(cls) -> list[type]:
        return [CommentsRelationManager]
```

## Class vars

| Var | Default | Role |
|-----|---------|------|
| `model` | `None` | Articulate (or other) model class |
| `slug` | plural of class name | URL segment; strips trailing `Resource`, snake_case + plural (`AuthorResource` → `authors`). Set `slug = "..."` to override. |
| `navigation_*` | sensible defaults | Sidebar label, icon, group, sort |
| `record_title_attribute` | `"id"` | How records introduce themselves |
| `permission_prefix` | slug | Ability prefix |

## Configure hooks

| Hook | Returns |
|------|---------|
| `form(form)` | Configured `Form` |
| `table(table)` | Configured `Table` |
| `infolist(infolist)` | Configured `Infolist` |
| `get_relations()` | Relation manager classes |

Call `Resource.get_form()`, `get_table()`, or `get_infolist()` when you need the built instance.

### Default table actions

If you leave action slots empty, `get_table()` wires:

- **Row:** View, Edit, Delete
- **Bulk:** Delete selected
- **Header:** Create

Override anytime:

```python
@classmethod
def table(cls, table: Table) -> Table:
    return (
        table.columns([TextColumn.make("title")])
        .header_actions([CreateAction.make()])
        .actions([EditAction.make(), DeleteAction.make()])
        .bulk_actions([DeleteBulkAction.make()])
    )
```

## Pages map

```python
PostResource.get_pages()
# {
#   "index":  "/posts",
#   "create": "/posts/create",
#   "edit":   "/posts/{id}/edit",
#   "view":   "/posts/{id}",
# }
```

Wire these into your router however your app mounts Orbit. The resource owns the *shape*; the app owns the HTTP.

## Permissions

Abilities are `{prefix}.view_any`, `.view`, `.create`, `.update`, `.delete`.

```python
PostResource.can_view_any(user)
PostResource.can_create(user)
PostResource.can_update(user, record)
PostResource.can_delete(user, record)
```

Resolution order looks for `can` / `has_permission` / `hasPermissionTo`, then admin flags, then a `permissions` set/list (including `"*"`). Pair with `almasix-permission` for the real deal.

## Relations

Return relation manager classes from `get_relations()` — see [Relation managers](/resources/managing-relationships/).

Next: [Pages](/navigation/custom-pages/), [Forms](/forms/overview/), [Tables](/tables/overview/).
