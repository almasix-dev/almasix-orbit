---
title: Tags input
description: TagsInput manages a list of string tags with chip UI, optional datalist suggestions, and reorderable chips for manual ordering.
---

## Introduction

TagsInput manages a list of string tags with chip UI, optional datalist suggestions, and reorderable chips for manual ordering.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic tags

Free-form tag entry.

```python
TagsInput.make('tags')
    .label('Tags')
```

![Orbit Basic tags (light)](/examples/light/forms/tags-input/basic.png)

![Orbit Basic tags (dark)](/examples/dark/forms/tags-input/basic.png)

## With suggestions

Datalist-backed autocomplete plus reorderable chips.

```python
TagsInput.make('tags')
    .label('Tags')
    .suggestions(['orbit', 'tables'])
    .reorderable()
```

![Orbit With suggestions (light)](/examples/light/forms/tags-input/suggestions.png)

![Orbit With suggestions (dark)](/examples/dark/forms/tags-input/suggestions.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
