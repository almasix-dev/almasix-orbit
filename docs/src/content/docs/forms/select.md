---
title: Select
description: Select fields render native or searchable dropdowns with static options, grouped options, or relationship-backed search.
---

## Introduction

Select fields render native or searchable dropdowns with static options, grouped options, or relationship-backed search. Searchable selects add a filter input; MultiSelect extends Select with multiple selection. Options can carry descriptions when used with Radio or CheckboxList patterns.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic select

Native dropdown with a static options map.

```python
Select.make('status')
    .label('Status')
    .options({'draft': 'Draft', 'published': 'Published'})
```

![Orbit Basic select (light)](/examples/light/forms/select/basic.png)

![Orbit Basic select (dark)](/examples/dark/forms/select/basic.png)

## Searchable select

Filterable list — ideal for long option sets.

```python
Select.make('status')
    .label('Status')
    .options({...})
    .searchable()
```

![Orbit Searchable select (light)](/examples/light/forms/select/searchable.png)

![Orbit Searchable select (dark)](/examples/dark/forms/select/searchable.png)

## Relationship select

Model-backed options (Filament-style). Without ``preload()``, searchable selects
load results via AJAX in pages of ``options_limit`` (default **50**). With
``preload()``, a capped set is loaded eagerly.

```python
Select.make('artist_id')
    .label('Artist')
    .relationship('artist', option_label='{name} - {country}')
    .searchable()
    # .preload()           # optional: eager load up to options_limit
    # .options_limit(50)   # optional: cap (default 50)
    # .get_option_label_from_record_using(lambda r: f"{r.name} ({r.id})")
```

``option_label`` formats labels from multiple columns (``{name} - {bio}``).
For full control use ``get_option_label_from_record_using``. Pass ``model=Artist``
when the related class is known and the owning resource model is not in render
context.

## Multi select

Multiple selection via MultiSelect.

```python
MultiSelect.make('tags')
    .label('Tags')
    .options({'orbit': 'Orbit', 'forms': 'Forms'})
```

![Orbit Multi select (light)](/examples/light/forms/select/multiple.png)

![Orbit Multi select (dark)](/examples/dark/forms/select/multiple.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
