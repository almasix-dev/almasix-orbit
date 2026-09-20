---
title: Tags input
description: TagsInput collects a list of string tags with chip chrome, optional suggestions, and separators.
---

## Introduction

`TagsInput` renders a chip row plus a text input. State may be a list/tuple of tags or a separator-joined string (default separator `,`). Suggestions use a native `<datalist>`. `.reorderable()` sets `data-reorderable` for client reordering. Dehydrated value is typically the joined string in the input; hosts often normalize to a list.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic tags input

Empty field with placeholder “Add tag…”. Users type and commit tags according to your Alpine/host bridge; chips reflect current state.

```python title="app/orbit/resources/example_resource.py"
TagsInput.make('tags')
    .label('Tags')
    .helper_text('Press enter to add a tag.')
```

![Orbit Basic tags input (light)](/examples/light/forms/tags-input/basic.png)

![Orbit Basic tags input (dark)](/examples/dark/forms/tags-input/basic.png)

## Suggestions

`.suggestions([...])` builds a datalist bound via `list=`. Browsers offer autocomplete while still allowing free tags.

```python title="app/orbit/resources/example_resource.py"
TagsInput.make('topics')
    .label('Topics')
    .suggestions(['orbit', 'schemas', 'forms', 'tables'])
```

![Orbit Suggestions (light)](/examples/light/forms/tags-input/suggestions.png)

![Orbit Suggestions (dark)](/examples/dark/forms/tags-input/suggestions.png)

## Custom separator

`.separator(';')` changes how string state is split and how chips are joined in the hidden/value input. Keep validation and API consumers aware of the chosen separator.

```python title="app/orbit/resources/example_resource.py"
TagsInput.make('labels')
    .label('Labels')
    .separator(';')
```

![Orbit Custom separator (light)](/examples/light/forms/tags-input/separator.png)

![Orbit Custom separator (dark)](/examples/dark/forms/tags-input/separator.png)

## Reorderable tags

`.reorderable()` marks the field for drag/reorder UI in panel assets (`data-reorderable="true"`).

```python title="app/orbit/resources/example_resource.py"
TagsInput.make('keywords')
    .label('Keywords')
    .reorderable()
    .suggestions(['seo', 'launch', 'beta'])
```

![Orbit Reorderable tags (light)](/examples/light/forms/tags-input/reorderable.png)

![Orbit Reorderable tags (dark)](/examples/dark/forms/tags-input/reorderable.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
