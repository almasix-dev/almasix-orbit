---
title: Rendering a form
description: Use Orbit Form outside a Resource — settings pages, wizards, and one-off flows.
---

Resources are convenient. They’re not mandatory.

A `Form` is a schema with validation and HTML. Mount it on a custom [page](/navigation/custom-pages/), a Conduit component, or a plain view handler. The same field kit that powers [Creating records](/resources/creating-records/) works here.

## Minimal

```python title="app/orbit/forms/settings.py"
from almasix.orbit.forms import Form, TextInput, Toggle

settings = (
    Form.make("settings")
    .schema([
        TextInput.make("site_name").required().max_length(80),
        Toggle.make("maintenance").label("Maintenance mode"),
    ])
)

settings.fill({"site_name": "Acme", "maintenance": False})
errors = settings.validate(request_data)
if not errors:
    save(settings.dehydrate())

html = settings.render(settings.get_state())
```

![Orbit standalone form (light)](/examples/light/components/form.png)

![Orbit standalone form (dark)](/examples/dark/components/form.png)

`fill` loads state, `validate` returns a `{field: [messages]}` map, `dehydrate` is the payload you persist. `render` walks the schema and emits `.or-field` chrome.

## On a custom page

```python title="app/orbit/pages/branding_page.py"
from almasix.orbit import Page
from almasix.orbit.forms import Form, TextInput


class BrandingPage(Page):
    navigation_label = "Branding"
    navigation_group = "Settings"

    def form(self) -> Form:
        return Form.make("branding").schema([
            TextInput.make("brand_name").required(),
            TextInput.make("primary_color").default("#f1511b"),
        ])
```

Wire `fill` / `validate` / `dehydrate` in your page action (or Conduit method). Orbit will not invent a database — it renders the fields and leaves persistence to you.

## Readonly mode

```python
form.readonly()          # Form-level flag
TextInput.make("slug").readonly()  # Field-level
```

Readonly fields still show up; they refuse to be edited. Handy for “review before publish” screens and for [View](/resources/viewing-records/) when you have not defined an infolist.

## Layouts

Nest [Section](/schemas/section/), [Grid](/schemas/grid/), [Tabs](/schemas/tabs/), and [Wizard](/schemas/wizard/) inside `.schema([...])`. The form does not care whether a child is a field or a layout — both are components.

```python title="app/orbit/forms/profile.py"
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.schemas import Section, Grid

Form.make("profile").schema([
    Section.make("identity")
    .heading("Identity")
    .schema([
            Grid.make().columns(2).schema([
            TextInput.make("first_name").required(),
            TextInput.make("last_name").required(),
        ]),
    ]),
])
```

## Why bother?

- Settings that aren’t a CRUD model
- Multi-step wizards that don’t map 1:1 to a resource
- Embedding a slice of Orbit UI inside a non-admin Conduit page

When you *do* have a model, prefer a [resource](/resources/overview/) so navigation, permissions, and table/form/infolist stay in one place.

Next: [Closures](/forms/closures/) · [Text input](/forms/text-input/) · [Validation](/forms/validation/).
