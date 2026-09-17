---
title: Select
description: Orbit Select field with options, groups, searchable UI, and relationships.
---

Pick one (or many) from a map of options — searchable when the list gets long.

## Standalone

```python
from almasix.orbit.forms import Form, Select

form = Form.make("demo").schema([
        Select.make("status")
            .options({"draft": "Draft", "published": "Published"})
            .searchable()
            .required()
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Select

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Select.make("status")
                .options({"draft": "Draft", "published": "Published"})
                .default("draft"),
            Select.make("author_id")
                .relationship(
                    "author",
                    "name",
                    search_columns=["name", "email"],
                    preload=True,
                )
                .searchable(),
            Select.make("city").options({
                "Europe": {"berlin": "Berlin", "paris": "Paris"},
                "Asia": {"tokyo": "Tokyo"},
            }),
        ])
```

## Key methods

- `.options(dict | callable | list[{label, options}])` — flat map, nested groups, or list of groups
- `.multiple() / .searchable()` — searchable adds Alpine filter + `data-searchable`
- `.relationship(name, title_attribute, *, search_columns, preload, modify_query, get_option_label)`
- `.create_option_form(...)` / `.edit_option_action(...)` — mount buttons for create/edit flows
- `.required() / .disabled(...) / .visible(...) / .live()`
- `.default(...) / .label(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).


## Preview

![Orbit forms/select (light)](/examples/light/forms/select.png)

![Orbit forms/select (dark)](/examples/dark/forms/select.png)
