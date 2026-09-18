---
title: Tags input
description: TagsInput manages a list of string tags with chip UI, optional datalist suggestions, and reorderable chips for manual ordering.
---

## Introduction

TagsInput manages a list of string tags with chip UI, optional datalist suggestions, and reorderable chips for manual ordering.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic tags

![Orbit Basic tags (light)](/examples/light/forms/tags-input/basic.png)

![Orbit Basic tags (dark)](/examples/dark/forms/tags-input/basic.png)

Free-form tag entry.

```python
TagsInput.make('tags').label('Tags')
```

## With suggestions

![Orbit With suggestions (light)](/examples/light/forms/tags-input/suggestions.png)

![Orbit With suggestions (dark)](/examples/dark/forms/tags-input/suggestions.png)

Datalist-backed autocomplete plus reorderable chips.

```python
TagsInput.make('tags').label('Tags').suggestions(['orbit', 'tables']).reorderable()
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
