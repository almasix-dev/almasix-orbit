---
title: Textarea
description: Textarea is the multiline string field with rows, cols, and optional autosize.
---

## Introduction

`Textarea` renders `<textarea class="or-textarea">` with Orbit label chrome. Default rows is 4 when unset. Use it for notes, bios, and JSON blobs that are not rich text. Prefer [Rich editor](/forms/rich-editor/) for HTML and [Markdown editor](/forms/markdown-editor/) for markdown-classed chrome.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic textarea

Labeled multiline field with default height. Placeholder and helper text work like TextInput.

```python title="app/orbit/resources/example_resource.py"
Textarea.make('notes')
    .label('Notes')
    .placeholder('Internal notes…')
    .helper_text('Not shown publicly.')
```

![Orbit Basic textarea (light)](/examples/light/forms/textarea/basic.png)

![Orbit Basic textarea (dark)](/examples/dark/forms/textarea/basic.png)

## Rows and columns

`.rows(n)` sets the HTML rows attribute. `.cols(n)` sets cols when you want a character-width hint (often ignored in full-width admin layouts but useful in constrained grids).

```python title="app/orbit/resources/example_resource.py"
Textarea.make('description')
    .label('Description')
    .rows(6)
    .cols(40)
```

![Orbit Rows and columns (light)](/examples/light/forms/textarea/rows.png)

![Orbit Rows and columns (dark)](/examples/dark/forms/textarea/rows.png)

## Autosize

`.autosize()` emits `data-autosize="true"` so client scripts can grow the textarea with content.

```python title="app/orbit/resources/example_resource.py"
Textarea.make('bio')
    .label('Bio')
    .autosize()
    .rows(3)
```

![Orbit Autosize (light)](/examples/light/forms/textarea/autosize.png)

![Orbit Autosize (dark)](/examples/dark/forms/textarea/autosize.png)

## Length validation

Combine `.required()`, `.min_length()`, and `.max_length()` for copy limits that `Form.validate` enforces.

```python title="app/orbit/resources/example_resource.py"
Textarea.make('summary')
    .label('Summary')
    .required()
    .min_length(20)
    .max_length(280)
```

![Orbit Length validation (light)](/examples/light/forms/textarea/validation.png)

![Orbit Length validation (dark)](/examples/dark/forms/textarea/validation.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
