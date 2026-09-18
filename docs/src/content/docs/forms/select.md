---
title: Select
description: Select fields render native or searchable dropdowns with static options, grouped options, or relationship-backed search.
---

## Introduction

Select fields render native or searchable dropdowns with static options, grouped options, or relationship-backed search. Searchable selects add a filter input; MultiSelect extends Select with multiple selection. Options can carry descriptions when used with Radio or CheckboxList patterns.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic select

![Orbit Basic select (light)](/examples/light/forms/select/basic.png)

![Orbit Basic select (dark)](/examples/dark/forms/select/basic.png)

Native dropdown with a static options map.

```python
Select.make('status').label('Status').options({'draft': 'Draft', 'published': 'Published'})
```

## Searchable select

![Orbit Searchable select (light)](/examples/light/forms/select/searchable.png)

![Orbit Searchable select (dark)](/examples/dark/forms/select/searchable.png)

Filterable list — ideal for long option sets.

```python
Select.make('status').label('Status').options({...}).searchable()
```

## Multi select

![Orbit Multi select (light)](/examples/light/forms/select/multiple.png)

![Orbit Multi select (dark)](/examples/dark/forms/select/multiple.png)

Multiple selection via MultiSelect.

```python
MultiSelect.make('tags').label('Tags').options({'orbit': 'Orbit', 'forms': 'Forms'})
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
