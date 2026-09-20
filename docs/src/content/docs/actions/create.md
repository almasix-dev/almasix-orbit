---
title: Create action
description: CreateAction preset — modal or page create, create another, and lifecycle hooks.
---

## Introduction

`CreateAction` is the header-slot preset for inserting records. Defaults: name `create`, label **Create**, plus icon, primary color.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import CreateAction
from almasix.orbit.forms import TextInput, Select

CreateAction.make()
    .modal()
    .modal_heading("New post")
    .form([
        TextInput.make("title").required(),
        Select.make("status").options({"draft": "Draft", "published": "Published"}),
    ])
    .create_another()
    .success_notification("Created")
```

![Orbit CreateAction (light)](/examples/light/actions/create.png)

![Orbit CreateAction (dark)](/examples/dark/actions/create.png)

Without `.modal()` / `.form(...)`, resources typically send the user to the create page via URL wiring.

## Create another

`.create_another()` tells the host to keep the modal open (or return to create) after a successful save so authors can add multiple rows. `.preserve_form_data_when_creating_another()` keeps field values between runs.

```python title="app/orbit/actions/create_another.py"
from almasix.orbit.actions import CreateAction

CreateAction.make()
    .modal()
    .create_another()
    .preserve_form_data_when_creating_another()
```

## Lifecycle

Same base hooks as `Action`, plus typical create persistence:

```python title="app/orbit/actions/create_lifecycle.py"
from almasix.orbit.actions import CreateAction

CreateAction.make()
    .mutate_data_using(lambda data, **_: {**data, "author_id": current_user_id()})
    .using(lambda data, **_: Post.create(**data))
    .after(lambda record, **_: index_search(record))
    .success_redirect_url(lambda record, **_: f"/posts/{record['id']}")
```

| Hook | Role |
|------|------|
| `.before` / `.after` | Side effects; `.halt()` / `.cancel()` stop the chain |
| `.mutate_data_using` | Transform modal / form `data` before persist |
| `.using` | Custom create body (replaces `.action`) |
| `.success_notification` / `.success_redirect_url` | Post-success UX |

## On a resource

```python title="app/orbit/resources/post_resource.py"
@classmethod
def table(cls, table):
    return table.header_actions([
        CreateAction.make().modal().form(cls.get_form().get_components()),
    ])
```

Empty header slots usually auto-wire `CreateAction` — see [Resources](/resources/overview/).
