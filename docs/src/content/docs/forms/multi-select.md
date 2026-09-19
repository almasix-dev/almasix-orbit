---
title: Multi select
description: MultiSelect is Select with multiple=True — choose many options, optionally searchable, limited, or reorderable.
---

## Introduction

MultiSelect is a thin subclass of [Select](/forms/select/) that sets `.multiple(True)` by default. Use it for tags, roles, and BelongsToMany-style attributes that still fit a fixed or relationship-backed option list. Everything on Select — search, preload, create option, min/max items, reorder — applies here.

Each variation below includes a short explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic multi select

Static options dehydrate as a list of selected keys. Cast the model column to a list/JSON array when persisting with Eloquent-style models.

```python title="app/orbit/resources/post_resource.py"
MultiSelect.make('tags')
    .label('Tags')
    .options({
        'orbit': 'Orbit',
        'forms': 'Forms',
        'tables': 'Tables',
    })
```

![Orbit Basic multi select (light)](/examples/light/forms/select/multiple.png)

![Orbit Basic multi select (dark)](/examples/dark/forms/select/multiple.png)

## Searchable multi select

`.searchable()` adds a filter over the option set — the same API as single Select, including relationship AJAX search when wired with `.relationship()`.

```python title="app/orbit/resources/post_resource.py"
MultiSelect.make('technologies')
    .label('Technologies')
    .options({
        'tailwind': 'Tailwind CSS',
        'alpine': 'Alpine.js',
        'laravel': 'Laravel',
        'livewire': 'Livewire',
    })
    .searchable()
```

![Orbit Searchable multi select (light)](/examples/light/forms/multi-select/searchable.png)

![Orbit Searchable multi select (dark)](/examples/dark/forms/multi-select/searchable.png)

## Limiting selection count

`.min_items()` and `.max_items()` constrain how many options may be chosen. Validation fails when the selection is outside the range — useful for “pick up to three topics” UX.

```python title="app/orbit/resources/post_resource.py"
MultiSelect.make('topics')
    .label('Topics')
    .options({
        'news': 'News',
        'product': 'Product',
        'engineering': 'Engineering',
        'design': 'Design',
    })
    .min_items(1)
    .max_items(3)
```

![Orbit Limiting selection count (light)](/examples/light/forms/multi-select/min-max-items.png)

![Orbit Limiting selection count (dark)](/examples/dark/forms/multi-select/min-max-items.png)

## Reorderable selections

`.reorderable()` lets users drag selected chips into order when sequence is meaningful (display priority, pipeline stages).

```python title="app/orbit/resources/post_resource.py"
MultiSelect.make('tags')
    .label('Tags')
    .reorderable()
    .options({
        'orbit': 'Orbit',
        'forms': 'Forms',
        'tables': 'Tables',
    })
```

![Orbit Reorderable selections (light)](/examples/light/forms/multi-select/reorderable.png)

![Orbit Reorderable selections (dark)](/examples/dark/forms/multi-select/reorderable.png)

## Relationship multi select

Combine MultiSelect with `.relationship()` for BelongsToMany-style pivots. Add `.searchable()` and optionally `.preload()` / `.options_limit()` as on single Select.

```python title="app/orbit/resources/post_resource.py"
MultiSelect.make('categories')
    .label('Categories')
    .relationship('categories', 'name')
    .searchable()
    .preload()
```

![Orbit Relationship multi select (light)](/examples/light/forms/multi-select/relationship.png)

![Orbit Relationship multi select (dark)](/examples/dark/forms/multi-select/relationship.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
