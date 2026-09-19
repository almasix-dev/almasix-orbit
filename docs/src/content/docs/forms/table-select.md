---
title: Table select
description: TableSelect is Select chrome with table-oriented CSS classes — not an embedded Orbit table.
---

## Introduction

**Honest scope:** `TableSelect` subclasses `Select` and only swaps classes to `or-field-TableSelect` and `or-select or-select-table`. It still renders a standard `<select>` (plus searchable UI when configured). There is **no** embedded table grid, column definitions, or row selection UI in the forms package yet. Use the same `.options()`, `.relationship()`, `.searchable()`, and `.multiple()` APIs as [Select](/forms/select/). Prefer [Modal table select](/forms/modal-table-select/) when you want a Browse affordance that the host can back with a real table later.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic table select

Options dehydrate like Select. CSS hooks let themes style the control as “table-like” without changing behavior.

```python title="app/orbit/resources/example_resource.py"
TableSelect.make('post_id')
    .label('Post')
    .options({
        '1': 'Launch announcement',
        '2': 'Host checklist',
        '3': 'Pricing update',
    })
```

![Orbit Basic table select (light)](/examples/light/forms/select/basic.png)

![Orbit Basic table select (dark)](/examples/dark/forms/select/basic.png)

## Searchable table select

`.searchable()` / `.native(False)` enable the same search input + Alpine filter path as Select.

```python title="app/orbit/resources/example_resource.py"
TableSelect.make('user_id')
    .label('User')
    .searchable()
    .options({'1': 'Ada', '2': 'Alan', '3': 'Grace'})
```

![Orbit Searchable table select (light)](/examples/light/forms/select/searchable.png)

![Orbit Searchable table select (dark)](/examples/dark/forms/select/searchable.png)

## Relationship-backed options

`.relationship()` resolves related models like Select — still into `<option>` elements, not table rows.

```python title="app/orbit/resources/example_resource.py"
TableSelect.make('author_id')
    .label('Author')
    .relationship('author', 'name')
    .searchable()
    .preload()
```

![Orbit Relationship-backed options (light)](/examples/light/forms/select/searchable.png)

![Orbit Relationship-backed options (dark)](/examples/dark/forms/select/searchable.png)

## Multiple selection

`.multiple()` emits a multi select with table CSS classes. True checkbox-table embedding remains deferred.

```python title="app/orbit/resources/example_resource.py"
TableSelect.make('category_ids')
    .label('Categories')
    .multiple()
    .options({'news': 'News', 'docs': 'Docs', 'blog': 'Blog'})
```

![Orbit Multiple selection (light)](/examples/light/forms/select/multiple.png)

![Orbit Multiple selection (dark)](/examples/dark/forms/select/multiple.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
