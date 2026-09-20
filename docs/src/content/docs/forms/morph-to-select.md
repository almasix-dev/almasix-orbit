---
title: Morph-to select
description: MorphToSelect lets the operator pick a type and then a record of that type — live-search included.
---

## Introduction

A **morph-to** field is two questions: *what kind of record?* and *which one?* `MorphToSelect` renders a type `<select>` next to a record `<select>`. Changing the type clears the chosen id and asks the server for that type’s options; typing in the search box filters those options.

State is a dict `{type, id}` (or a `"type:id"` string). `.type_attribute()` / `.id_attribute()` rename the keys when your columns are not `type` / `id`.

For large lists, skip static `options` and give Orbit a loader:

```python title="app/orbit/resources/comment_resource.py"
MorphToSelect.make("commentable")
    .searchable()
    .types([{"type": "post", "label": "Post"}, {"type": "video", "label": "Video"}])
    .options_using(lambda type="", search="", **_: load_commentables(type, search))
```

The create/edit host calls that loader as `callback(type=..., search=...)` whenever the type changes or the operator types.

Each variation below includes the fluent API and light/dark screenshots of the rendered control.

## Basic morph-to select

Provide typed option maps so the id select can show records for the chosen morph type.

```python title="app/orbit/resources/example_resource.py"
MorphToSelect.make('assignee')
    .label('Assignee')
    .types([
        {
            'type': 'user',
            'label': 'User',
            'options': {'1': 'Ada Lovelace', '2': 'Alan Turing'},
        },
        {
            'type': 'team',
            'label': 'Team',
            'options': {'10': 'Platform', '11': 'Design'},
        },
    ])
```

![Orbit Basic morph-to select (light)](/examples/light/forms/morph-to-select/basic.png)

![Orbit Basic morph-to select (dark)](/examples/dark/forms/morph-to-select/basic.png)

## Searchable wrapper

`.searchable()` adds `data-searchable` on the wrapper for host search behavior across the morph selects.

```python title="app/orbit/resources/example_resource.py"
MorphToSelect.make('owner')
    .label('Owner')
    .searchable()
    .types([
        {'type': 'user', 'label': 'User', 'options': {'1': 'Ada'}},
        {'type': 'org', 'label': 'Organization', 'options': {'5': 'Acme'}},
    ])
```

![Orbit Searchable wrapper (light)](/examples/light/forms/morph-to-select/searchable.png)

![Orbit Searchable wrapper (dark)](/examples/dark/forms/morph-to-select/searchable.png)

## Custom type and id attributes

When your polymorphic columns are not `type` / `id`, remap with `.type_attribute()` and `.id_attribute()` so dict state round-trips correctly.

```python title="app/orbit/resources/example_resource.py"
MorphToSelect.make('notable')
    .label('Notable')
    .type_attribute('notable_type')
    .id_attribute('notable_id')
    .types(['App\\Models\\Post', 'App\\Models\\Video'])
```

![Orbit Custom type and id attributes (light)](/examples/light/forms/morph-to-select/attributes.png)

![Orbit Custom type and id attributes (dark)](/examples/dark/forms/morph-to-select/attributes.png)

## Class-string types

Passing bare class strings builds type options from the final segment of each name; populate id options separately via `.options()` or per-type maps.

```python title="app/orbit/resources/example_resource.py"
MorphToSelect.make('subject')
    .label('Subject')
    .types([
        'App\\Models\\User',
        'App\\Models\\Team',
    ])
    .options({'1': 'Ada', '2': 'Grace'})
```

![Orbit Class-string types (light)](/examples/light/forms/morph-to-select/class-strings.png)

![Orbit Class-string types (dark)](/examples/dark/forms/morph-to-select/class-strings.png)

## Live search

`.searchable()` plus `.options_using(...)` is the production path. The host keeps `morph_search` per field, re-renders the id select with the filtered map, and clears the search when the type changes.

```python title="app/orbit/resources/example_resource.py"
def load_owners(type: str = "", search: str = "", **_: object) -> dict[str, str]:
    rows = users() if type == "user" else teams()
    needle = search.casefold()
    return {
        str(row["id"]): row["name"]
        for row in rows
        if not needle or needle in row["name"].casefold()
    }

MorphToSelect.make("owner")
    .label("Owner")
    .searchable()
    .types([{"type": "user", "label": "User"}, {"type": "team", "label": "Team"}])
    .options_using(load_owners)
```

![Orbit Live search (light)](/examples/light/forms/morph-to-select/live-search.png)

![Orbit Live search (dark)](/examples/dark/forms/morph-to-select/live-search.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
