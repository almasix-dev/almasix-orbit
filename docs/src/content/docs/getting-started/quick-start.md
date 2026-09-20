---
title: Quick start
description: Build your first Orbit panel and resource — small enough to fit in your head, complete enough to show the loop.
---

Let’s build a tiny Posts admin — one resource, one panel, done.

## 1. Define a resource

```python title="app/orbit/admin/resources/post_resource.py"
from almasix.orbit import Resource
from almasix.orbit.forms import Form, TextInput, Textarea
from almasix.orbit.tables import Table, TextColumn
from almasix.orbit.infolists import Infolist, TextEntry

from app.models.post import Post


class PostResource(Resource):
    model = Post
    navigation_label = "Posts"
    navigation_group = "Content"
    navigation_sort = 1
    navigation_icon = "heroicon-o-pencil-square"
    permission_prefix = "posts"
    record_title_attribute = "title"

    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            TextInput.make("title").required().max_length(200),
            TextInput.make("slug").required(),
            Textarea.make("body").rows(8),
        ])

    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            TextColumn.make("title").searchable().sortable(),
            TextColumn.make("slug").searchable(),
        ])

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist.schema([
            TextEntry.make("title"),
            TextEntry.make("slug").copyable(),
            TextEntry.make("body").prose(),
        ])
```

Orbit fills row / bulk / header actions for you when you leave those slots empty — view, edit, delete, delete selected, and create.

## 2. Configure the panel

After `smith orbit:install`, edit the generated panel file (not the provider):

```python title="app/orbit/admin/panel.py"
from almasix.orbit import Panel, PanelRegistry

from app.orbit.admin.resources.post_resource import PostResource


def register_admin_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("admin")
        .path("orbit")
        .brand_name("Acme Admin")
        .primary("#f1511b")
        .resources([PostResource])
        .login()
        .discover_panel_dirs()
    )
    registry.register(panel)
    return panel
```

`OrbitPanelProvider` already calls `register_app_orbit_panels(...)` on boot, so this file is picked up automatically. Keep brand, resources, and plugins here — leave the provider thin. See [Installation](/getting-started/installation/).

## 3. Render the shell

When you need the HTML chrome — sidebar, brand, Orbit assets — ask the panel:

```python
panel = app.make(PanelRegistry).get("admin")
html = panel.render_shell("<p>Welcome.</p>", user=request.user)
```

Navigation items come from resources and pages: label, icon, group, URL, sort.

## 4. Sanity-check with LiveResource

```python title="tests/orbit/test_post_resource.py"
from almasix.orbit.testing import LiveResource

from app.orbit.post_resource import PostResource


def test_post_resource_shape():
    live = LiveResource(PostResource)
    live.assert_form_has_field("title")
    live.assert_table_has_column("title")
    errors = live.fill_form({})
    assert "title" in errors
```

You wrote Python. The panel has a sidebar entry, a form, and a table. That’s the whole game.

Dive deeper: [Panels](/panels/configuration/), [Resources](/resources/overview/), [Forms](/forms/overview/), [Tables](/tables/overview/), [Infolists](/infolists/overview/).
