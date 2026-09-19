---
title: Repeater
description: Repeater repeats a nested schema as a list of item dicts with add, remove, clone, reorder, and table layouts.
---

## Introduction

`Repeater` stores state as a list of dictionaries (or a simple list when using `.simple()`). Each item renders the nested schema with Conduit actions `addRepeaterItem`, `removeRepeaterItem`, `cloneRepeaterItem`, and `moveRepeaterItem`. Use it for line items, addresses, FAQ entries, and any JSON array of structured rows. Relationship-backed variants belong on [Relationship repeater](/forms/relationship-repeater/); typed block pickers belong on [Builder](/forms/builder/).

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic repeater

Provide a `.schema([...])` of child fields. `.default_items(1)` seeds one empty row when state is empty. Child state paths are read from each item dict by field name.

```python title="app/orbit/resources/example_resource.py"
from almasix.orbit.forms import Repeater, TextInput

Repeater.make('items')
    .label('Line items')
    .schema([
        TextInput.make('name').label('Name').required(),
        TextInput.make('qty').label('Qty').numeric(),
    ])
    .default_items(1)
```

![Orbit Basic repeater (light)](/examples/light/forms/repeater/basic.png)

![Orbit Basic repeater (dark)](/examples/dark/forms/repeater/basic.png)

## Simple repeater

`.simple(field)` uses a single child field per row (class `or-repeater-simple`) instead of a multi-field schema — handy for tag-like lists that still need add/remove chrome.

```python title="app/orbit/resources/example_resource.py"
Repeater.make('aliases')
    .label('Aliases')
    .simple(TextInput.make('value').placeholder('Alias'))
    .default_items(1)
```

![Orbit Simple repeater (light)](/examples/light/forms/repeater/simple.png)

![Orbit Simple repeater (dark)](/examples/dark/forms/repeater/simple.png)

## Item limits

`.min_items()` / `.max_items()` emit data attributes and disable Add when at max. `.default_items()` controls the empty-state seed count.

```python title="app/orbit/resources/example_resource.py"
Repeater.make('phones')
    .label('Phone numbers')
    .simple(TextInput.make('number').tel())
    .default_items(1)
    .min_items(1)
    .max_items(3)
```

![Orbit Item limits (light)](/examples/light/forms/repeater/item-limits.png)

![Orbit Item limits (dark)](/examples/dark/forms/repeater/item-limits.png)

## Add and remove controls

`.addable(False)` hides the Add button; `.deletable(False)` hides Remove. `.add_action_label()` customizes the Add button text.

```python title="app/orbit/resources/example_resource.py"
Repeater.make('addresses')
    .label('Addresses')
    .schema([TextInput.make('line1').label('Line 1')])
    .add_action_label('Add address')
    .deletable(True)
```

![Orbit Add and remove controls (light)](/examples/light/forms/repeater/actions.png)

![Orbit Add and remove controls (dark)](/examples/dark/forms/repeater/actions.png)

## Cloneable, reorderable, collapsible

`.cloneable()` duplicates an item; `.reorderable()` adds up/down move buttons; `.collapsible()` wraps each item in Alpine collapse state with Expand/Collapse.

```python title="app/orbit/resources/example_resource.py"
Repeater.make('sections')
    .label('Sections')
    .schema([TextInput.make('heading').label('Heading')])
    .cloneable()
    .reorderable()
    .collapsible()
```

![Orbit Cloneable, reorderable, collapsible (light)](/examples/light/forms/repeater/cloneable-reorderable.png)

![Orbit Cloneable, reorderable, collapsible (dark)](/examples/dark/forms/repeater/cloneable-reorderable.png)

## Item labels

`.item_label()` accepts a string or callable. Callables receive `index`, `item` / `state`, plus render context — use them to show “Address #2” or a title from the row.

```python title="app/orbit/resources/example_resource.py"
Repeater.make('contacts')
    .label('Contacts')
    .schema([TextInput.make('name').label('Name')])
    .item_label(lambda index, item=None, **_: (item or {}).get('name') or f'Contact {index + 1}')
```

![Orbit Item labels (light)](/examples/light/forms/repeater/item-label.png)

![Orbit Item labels (dark)](/examples/dark/forms/repeater/item-label.png)

## Grid layout

`.grid(columns)` sets `data-grid` so CSS can arrange item fields in columns without changing the nested schema API.

```python title="app/orbit/resources/example_resource.py"
Repeater.make('features')
    .label('Features')
    .schema([
        TextInput.make('title').label('Title'),
        TextInput.make('icon').label('Icon'),
    ])
    .grid(2)
```

![Orbit Grid layout (light)](/examples/light/forms/repeater/grid.png)

![Orbit Grid layout (dark)](/examples/dark/forms/repeater/grid.png)

## Table layout

`.table([...])` adds a table header row and `or-repeater-table` chrome for spreadsheet-like entry. Column labels are presentation only — field order still comes from `.schema()`.

```python title="app/orbit/resources/example_resource.py"
Repeater.make('items')
    .label('Items')
    .table(['Name', 'Qty'])
    .schema([
        TextInput.make('name'),
        TextInput.make('qty').numeric(),
    ])
```

![Orbit Table layout (light)](/examples/light/forms/repeater/table.png)

![Orbit Table layout (dark)](/examples/dark/forms/repeater/table.png)

## Relationship metadata on Repeater

`.relationship(name)` sets `data-relationship` and stores the relationship name for hydrate/mutate hooks. Prefer `RelationshipRepeater` when the field is always relation-backed; use these mutators on either class.

```python title="app/orbit/resources/example_resource.py"
Repeater.make('comments')
    .relationship('comments')
    .schema([TextInput.make('body').label('Body')])
    .mutate_relationship_data_before_fill(lambda data, **_: data)
```

![Orbit Relationship metadata on Repeater (light)](/examples/light/forms/repeater/relationship.png)

![Orbit Relationship metadata on Repeater (dark)](/examples/dark/forms/repeater/relationship.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, `.required()`, and repeater `.item_label()` where applicable — see [Form closures](/forms/closures/).
