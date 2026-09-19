---
title: Markdown editor
description: MarkdownEditor is a Textarea with markdown editor chrome classes — no separate preview toolbar in the forms package today.
---

## Introduction

**Honest scope:** `MarkdownEditor` subclasses `Textarea` and only renames CSS classes to `or-field-MarkdownEditor` and `or-textarea or-editor or-editor-markdown`. There is no markdown toolbar, split preview, or parser in Python. Use it when you want semantic markdown chrome and the same `.rows()`, `.autosize()`, and `.cols()` helpers as textarea, then wire preview in panel assets if needed.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic markdown editor

Drop-in multiline field labeled for markdown content. Dehydrates the raw markdown string like a textarea.

```python title="app/orbit/resources/example_resource.py"
MarkdownEditor.make('readme')
    .label('README')
    .rows(10)
    .helper_text('GitHub-flavored markdown.')
```

![Orbit Basic markdown editor (light)](/examples/light/forms/markdown-editor/basic.png)

![Orbit Basic markdown editor (dark)](/examples/dark/forms/markdown-editor/basic.png)

## Autosize and columns

`.autosize()` adds `data-autosize="true"` for client growth. `.cols()` sets the HTML `cols` attribute when you want a fixed character width hint.

```python title="app/orbit/resources/example_resource.py"
MarkdownEditor.make('changelog')
    .label('Changelog')
    .autosize()
    .cols(80)
```

![Orbit Autosize and columns (light)](/examples/light/forms/markdown-editor/autosize.png)

![Orbit Autosize and columns (dark)](/examples/dark/forms/markdown-editor/autosize.png)

## Required markdown

Shared Field validation applies — `.required()`, `.min_length()`, and custom `.rules()` work the same as Textarea.

```python title="app/orbit/resources/example_resource.py"
MarkdownEditor.make('release_notes')
    .label('Release notes')
    .required()
    .min_length(20)
```

![Orbit Required markdown (light)](/examples/light/forms/markdown-editor/required.png)

![Orbit Required markdown (dark)](/examples/dark/forms/markdown-editor/required.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
