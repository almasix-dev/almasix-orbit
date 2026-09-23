---
title: Tags input
description: TagsInput collects a list of string tags with chip chrome, optional suggestions, and separators.
---

## Introduction

`TagsInput` stores an ordered list of string tags. Users type in a draft field and commit with **Enter**, **Tab**, or your configured separator (default `,`). Each tag becomes a removable chip inside a single bordered control. Suggestions use a native `<datalist>`. State is synced to the form host as a list — cast the model attribute to an array/JSON list.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic tags input

Empty field with placeholder “New tag”. Press Enter to add a chip; click × on a chip to remove it. Backspace on an empty draft removes the last tag.

```python title="app/orbit/resources/example_resource.py"
TagsInput.make('tags')
    .label('Tags')
    .helper_text('Press Enter to add a tag.')
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

`.separator(';')` changes how string state is split when hydrating and which character (besides Enter/Tab) commits a draft tag. Prefer list state on the model when you can.

```python title="app/orbit/resources/example_resource.py"
TagsInput.make('labels')
    .label('Labels')
    .separator(';')
```

![Orbit Custom separator (light)](/examples/light/forms/tags-input/separator.png)

![Orbit Custom separator (dark)](/examples/dark/forms/tags-input/separator.png)

## Split keys

`.split_keys([...])` adds extra keys that commit the draft tag. Enter always commits; Tab and your `.separator()` are included by default.

```python title="app/orbit/resources/example_resource.py"
TagsInput.make('keywords')
    .label('Keywords')
    .split_keys([' ', ','])
```

## Reorderable tags

`.reorderable()` marks the field for client reordering (`data-reorderable`). Use when tag order is meaningful.

```python title="app/orbit/resources/example_resource.py"
TagsInput.make('keywords')
    .label('Keywords')
    .reorderable()
```

![Orbit Reorderable tags (light)](/examples/light/forms/tags-input/reorderable.png)

![Orbit Reorderable tags (dark)](/examples/dark/forms/tags-input/reorderable.png)
