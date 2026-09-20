---
title: Resource page hosts
description: ListRecords, CreateRecord, EditRecord, and ViewRecord — the HTML hosts Orbit mounts for every resource.
---

A **resource page host** is the Python class that turns a [resource](/resources/overview/) into HTML for one route. Register a resource on a panel and Orbit mounts four hosts under the panel path:

| Host | Typical URL | What it paints |
|------|-------------|----------------|
| `ListRecords` | `/admin/posts` | Heading, header actions, optional tabs, the resource [table](/tables/overview/) |
| `CreateRecord` | `/admin/posts/create` | Heading plus the resource [form](/forms/overview/) and a Create button |
| `EditRecord` | `/admin/posts/{id}/edit` | Record title, the same form, Save, plus [relation managers](/resources/managing-relationships/) |
| `ViewRecord` | `/admin/posts/{id}` | Record title, the [infolist](/infolists/overview/), plus relation managers |

You rarely construct these by hand. Override them when you need custom tabs, extra chrome, or a different heading.

```python title="app/orbit/pages/post_list.py"
from almasix.orbit.panels.pages import ListRecords, CreateRecord, EditRecord, ViewRecord, Tab

from app.orbit.resources.post_resource import PostResource


class PostList(ListRecords):
    resource = PostResource


html = PostList.render(records=posts, active_tab="published")
```

![Orbit List page host (light)](/examples/light/resources/pages/list.png)

![Orbit List page host (dark)](/examples/dark/resources/pages/list.png)

## Bind a custom host on the resource

Point the resource at your subclass so the panel routes use it:

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit import Resource
from almasix.orbit.panels.pages import ListRecords, Tab


class PostList(ListRecords):
    resource = PostResource  # set after the class exists, or assign list_page

    @classmethod
    def get_tabs(cls):
        return [
            Tab("all").label("All"),
            Tab("published")
            .label("Published")
            .icon("heroicon-o-check")
            .badge(3)
            .badge_color("success")
            .modify_query_using(lambda rows: [r for r in rows if r.get("published")]),
        ]


class PostResource(Resource):
    model = Post
    list_page = PostList
```

`Tab.modify_query_using` receives the current row list (in-memory or already loaded) and must return a list. The first tab is active unless you pass `active_tab=...` to `render`.

![Orbit List tabs (light)](/examples/light/resources/pages/tabs.png)

![Orbit List tabs (dark)](/examples/dark/resources/pages/tabs.png)

## Create, edit, and view

`CreateRecord.render(state=...)` fills the resource form and wraps it in `<form class="or-form">` with a Create submit. Seed-list resources with `records_mutable = False` render a muted note instead of a writable form.

```python title="app/orbit/pages/post_create.py"
from almasix.orbit.panels.pages import CreateRecord

from app.orbit.resources.post_resource import PostResource


class PostCreate(CreateRecord):
    resource = PostResource


html = PostCreate.render(state={"title": "", "status": "draft"})
```

![Orbit Create page host (light)](/examples/light/resources/pages/create.png)

![Orbit Create page host (dark)](/examples/dark/resources/pages/create.png)

`EditRecord.render(record=..., state=...)` hydrates the form from the record when you omit `state`. The heading uses [`get_record_title`](/resources/overview/#record-titles). Relation managers render below the form.

![Orbit Edit page host (light)](/examples/light/resources/pages/edit.png)

![Orbit Edit page host (dark)](/examples/dark/resources/pages/edit.png)

`ViewRecord.render(record=...)` paints the infolist (or a readonly form projection when `infolist()` is empty) plus the same relation managers.

![Orbit View page host (light)](/examples/light/resources/pages/view.png)

![Orbit View page host (dark)](/examples/dark/resources/pages/view.png)

## Tab API

| Method | Role |
|--------|------|
| `Tab(id)` | Stable id used in `data-tab` and `setTab(...)` |
| `.label(text)` | Button text (defaults to a title-cased id) |
| `.icon(name)` | Heroicon before the label |
| `.badge(value)` | Static value, or a callable evaluated at render (`records` is in context) |
| `.badge_color(color)` | Color token on the badge |
| `.modify_query_using(fn)` | Filter the row list for this tab |

Live list state (`table_search`, `table_sort`, pagination, selection) lives on the Conduit list host — see [Listing records](/resources/listing-records/).

## Scaffolding and discovery

```bash title="terminal"
smith make:orbit-resource Post --panel=admin
smith make:orbit-resource Post --panel=admin --model=Post --generate
```

The command writes `app/orbit/{panel}/resources/post_resource.py`. Call `panel.discover_resources(...).load_discovered()` to import every module under that path so you do not have to list each class in `panel.resources([...])`.

## Related pages

- [Listing records](/resources/listing-records/) — search, sort, filters, and tabs on the index
- [Creating records](/resources/creating-records/) — submit, defaults, and mutability
- [Editing records](/resources/editing-records/)
- [Viewing records](/resources/viewing-records/)
