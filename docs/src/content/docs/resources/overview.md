---
title: Overview
description: CRUD resources — forms, tables, infolists, permissions, and page routes for one model.
---

A **resource** is one admin surface for a model. It owns the form (create/edit), table (index), optional infolist (view), permissions, and the usual index / create / edit / view routes. Register the resource class on a [panel](/panels/configuration/); Orbit mounts the pages under the panel path.

```python title="app/orbit/resources/post_resource.py"
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
| `model_label` / `plural_model_label` | derived from slug | Singular / plural wording in page headings |
| `global_search_attributes` | `()` | Attributes matched by [global search](/resources/global-search/) |
| `global_search_result_details` | `()` | Attributes shown under a search result |
| `global_search_result_limit` | `5` | Most results this resource contributes |
| `soft_deletes` | `False` | Adds a trashed filter plus restore / force-delete actions |
| `permission_prefix` | slug | Ability prefix |

### Record titles

`record_title_attribute` names the field that identifies a record. Orbit uses it for the view and edit page headings, the last breadcrumb, and global search results:

```python
PostResource.get_record_title({"id": 3, "title": "Launch Orbit"})   # "Launch Orbit"
PostResource.get_record_title({"id": 3, "title": ""})               # "Post #3"
```

Override `get_record_title(record)` when the title is computed from several fields.

## Configure hooks

| Hook | Returns |
|------|---------|
| `form(form)` | Configured `Form` |
| `table(table)` | Configured `Table` |
| `infolist(infolist)` | Configured `Infolist` |
| `get_relations()` | Relation manager classes |

Call `Resource.get_form()`, `get_table()`, or `get_infolist()` when you need the built instance.

## Scaffolding (`make:orbit-resource`)

```bash title="terminal"
smith make:orbit-resource Post --panel=admin
smith make:orbit-resource Post --model=Post --generate
# or: smith orbit:resource Post -G --model=app.models.post.Post
```

| Option | Role |
|--------|------|
| `--panel=` | Target panel package (`app/orbit/{id}/resources/`) |
| `--model=` | ORM model (bare `Post` or `app.models.post.Post`); also guessed from the resource name |
| `--generate` / `-G` | Reflect `Schema.columns` on the model’s table and stub form fields + table columns |
| `--force` | Overwrite an existing file |

Without `--generate`, the stub still uses a `title` TextInput / TextColumn. When a model resolves and the CLI is interactive, Orbit asks whether to generate from the database. Review and adjust the guessed types afterward (especially enums and relationships).

### Default table actions

If you leave action slots empty, `get_table()` wires:

- **Row:** View, Edit, Delete
- **Bulk:** Delete selected
- **Header:** Create

Override anytime:

```python title="app/orbit/resources/post_resource.py"
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

```python title="app/orbit/resources/post_resource.py"
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

```python title="app/orbit/resources/post_resource.py"
PostResource.can_view_any(user)
PostResource.can_create(user)
PostResource.can_update(user, record)
PostResource.can_delete(user, record)
```

Resolution order looks for `can` / `has_permission` / `hasPermissionTo`, then admin flags, then a `permissions` set/list (including `"*"`). Pair with `almasix-permission` for the real deal.

## Relations

Return relation manager classes from `get_relations()`. Orbit renders each one on the view and edit pages — see [Relation managers](/resources/managing-relationships/).

## Soft deletes

```python
class PostResource(Resource):
    soft_deletes = True
```

The default table gains a trashed filter ("Without trashed" / "With trashed" / "Only trashed") and restore plus force-delete row actions that appear only on trashed rows. List and view hosts learn the `restore` action, which calls the model's `restore()` when it has one and otherwise clears `deleted_at`.

## Global search

Declare `global_search_attributes` and the resource joins the panel's topbar search box — see [Global search](/resources/global-search/).

Next: [Listing records](/resources/listing-records/), [Forms](/forms/overview/), [Tables](/tables/overview/), [Infolists](/infolists/overview/).
