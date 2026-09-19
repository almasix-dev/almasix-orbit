---
title: Morph-to select
description: MorphToSelect pairs a type select with an id select for polymorphic assignments.
---

## Introduction

`MorphToSelect` subclasses `Select` but renders two `<select>` elements inside `or-morph-to-select` (type + id), with Alpine `orbitMorphToSelect`. State may be a dict `{type, id}`, a `"Type:id"` string, or an id-only value. Configure types via `.types([...])` as model class strings or maps with `type` / `label` / `options`. `.type_attribute()` / `.id_attribute()` rename the keys used when state is a dict.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

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

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
