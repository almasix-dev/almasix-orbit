---
title: Toggle buttons
description: ToggleButtons render Select options as a grouped set of radio-styled button chips.
---

## Introduction

`ToggleButtons` subclasses `Select` but does not render a `<select>`. Each option becomes a labeled radio inside `or-toggle-buttons`, with `is-active` on the selected chip. State is a single option key. Use it for compact status, visibility, or size pickers where a dropdown feels heavy. **Note:** Field helpers `.descriptions()` and `.options_columns()` exist on the base class for Radio/CheckboxList; ToggleButtons’ render loop currently ignores those and only paints labels.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic toggle buttons

Provide `.options({value: label})`. The first selection dehydrates as that key string.

```python title="app/orbit/resources/example_resource.py"
ToggleButtons.make('status')
    .label('Status')
    .options({
        'draft': 'Draft',
        'review': 'In review',
        'published': 'Published',
    })
```

![Orbit Basic toggle buttons (light)](/examples/light/forms/toggle-buttons/basic.png)

![Orbit Basic toggle buttons (dark)](/examples/dark/forms/toggle-buttons/basic.png)

## Boolean Yes / No

`.boolean()` sets options to `{1: "Yes", 0: "No"}` — same helper as Select/Radio.

```python title="app/orbit/resources/example_resource.py"
ToggleButtons.make('featured')
    .label('Featured')
    .boolean()
```

![Orbit Boolean Yes / No (light)](/examples/light/forms/toggle-buttons/boolean.png)

![Orbit Boolean Yes / No (dark)](/examples/dark/forms/toggle-buttons/boolean.png)

## Required selection

`.required()` injects a required rule and asterisk. Disable the whole group with `.disabled()` or `.disabled_on('view')`.

```python title="app/orbit/resources/example_resource.py"
ToggleButtons.make('priority')
    .label('Priority')
    .options({'low': 'Low', 'medium': 'Medium', 'high': 'High'})
    .required()
```

![Orbit Required selection (light)](/examples/light/forms/toggle-buttons/required.png)

![Orbit Required selection (dark)](/examples/dark/forms/toggle-buttons/required.png)

## Enum options

`.enum(MyEnum)` populates options from an Enum’s values → title-cased names, inherited from Field.

```python title="app/orbit/resources/example_resource.py"
from enum import Enum

class Size(Enum):
    S = 's'
    M = 'm'
    L = 'l'

ToggleButtons.make('size')
    .label('Size')
    .enum(Size)
```

![Orbit Enum options (light)](/examples/light/forms/toggle-buttons/enum.png)

![Orbit Enum options (dark)](/examples/dark/forms/toggle-buttons/enum.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
