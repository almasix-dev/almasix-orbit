---
title: Rendering a form
description: Use Orbit Form outside a Resource — settings pages, wizards, and one-off flows.
---

Resources are convenient. They’re not mandatory.

A `Form` is just a schema with validation and HTML. Mount it on a custom [Page](/navigation/custom-pages/), a Conduit component, or a plain view handler.

## Minimal

```python
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

## On a custom page

```python
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

Wire `fill` / `validate` / `dehydrate` in your page action (or Conduit method). Orbit won’t invent a database for you — it will happily render the fields.

## Readonly mode

```python
form.readonly()          # Form-level flag
TextInput.make("slug").readonly()  # Field-level
```

Readonly fields still show up; they just refuse to be edited. Handy for “review before publish” screens.

## Why bother?

- Settings that aren’t a CRUD model
- Multi-step wizards that don’t map 1:1 to a Resource
- Embedding a slice of Orbit UI inside a non-admin Conduit page

When you *do* have a model, prefer a [Resource](/resources/overview/) so navigation, permissions, and table/form/infolist stay in one place.

Next: [Closures](/forms/closures/) · [Field reference](/forms/text-input/).
