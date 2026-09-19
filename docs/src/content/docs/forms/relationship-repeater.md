---
title: Relationship repeater
description: RelationshipRepeater is a Repeater that defaults relationship metadata to the field name for related-model rows.
---

## Introduction

`RelationshipRepeater` subclasses `Repeater` and, on render, ensures `_relationship_name` defaults to the field name, then swaps the CSS class to `or-field-RelationshipRepeater`. Persistence, create/update of related models, and query loading remain the resource/host’s job — this field owns nested UI chrome plus mutate hooks. Prefer it over plain Repeater when rows map to `hasMany` / similar relations.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic relationship repeater

Name the field after the relation (or call `.relationship('name')` explicitly). Nested schema fields map to related attributes.

```python title="app/orbit/resources/example_resource.py"
from almasix.orbit.forms import RelationshipRepeater, TextInput, Textarea

RelationshipRepeater.make('comments')
    .label('Comments')
    .relationship('comments')
    .schema([
        TextInput.make('author').label('Author'),
        Textarea.make('body').label('Body').required(),
    ])
    .default_items(0)
    .add_action_label('Add comment')
```

![Orbit Basic relationship repeater (light)](/examples/light/forms/relationship-repeater/basic.png)

![Orbit Basic relationship repeater (dark)](/examples/dark/forms/relationship-repeater/basic.png)

## Mutate before fill

`.mutate_relationship_data_before_fill()` runs through `apply_mutate_before_fill` when the host hydrates related rows into form state. Return the transformed list/dict payload.

```python title="app/orbit/resources/example_resource.py"
RelationshipRepeater.make('items')
    .relationship('items')
    .schema([TextInput.make('sku'), TextInput.make('qty').numeric()])
    .mutate_relationship_data_before_fill(
        lambda data, **_: [{**row, 'qty': int(row.get('qty') or 0)} for row in (data or [])]
    )
```

![Orbit Mutate before fill (light)](/examples/light/forms/relationship-repeater/mutate-fill.png)

![Orbit Mutate before fill (dark)](/examples/dark/forms/relationship-repeater/mutate-fill.png)

## Mutate before create and save

`.mutate_relationship_data_before_create()` and `.mutate_relationship_data_before_save()` let you inject owner keys, timestamps, or normalized attributes before the host persists rows.

```python title="app/orbit/resources/example_resource.py"
RelationshipRepeater.make('tasks')
    .relationship('tasks')
    .schema([TextInput.make('title').required()])
    .mutate_relationship_data_before_create(
        lambda data, record=None, **_: {**data, 'project_id': getattr(record, 'id', None)}
    )
    .mutate_relationship_data_before_save(
        lambda data, **_: {**data, 'title': str(data.get('title', '')).strip()}
    )
```

![Orbit Mutate before create and save (light)](/examples/light/forms/relationship-repeater/mutate.png)

![Orbit Mutate before create and save (dark)](/examples/dark/forms/relationship-repeater/mutate.png)

## Clone and reorder related rows

All Repeater interaction helpers work — clone/reorder/collapse still emit the same wire actions; the host decides whether clone creates a new related model.

```python title="app/orbit/resources/example_resource.py"
RelationshipRepeater.make('milestones')
    .relationship('milestones')
    .schema([TextInput.make('name'), TextInput.make('due_on')])
    .cloneable()
    .reorderable()
```

![Orbit Clone and reorder related rows (light)](/examples/light/forms/repeater/cloneable-reorderable.png)

![Orbit Clone and reorder related rows (dark)](/examples/dark/forms/repeater/cloneable-reorderable.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, `.required()`, and repeater `.item_label()` where applicable — see [Form closures](/forms/closures/).
