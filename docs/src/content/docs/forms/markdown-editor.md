---
title: Markdown editor
description: MarkdownEditor styles a Textarea for markdown source editing.
---

## Introduction

MarkdownEditor styles a Textarea for markdown source editing. Pair with a preview prime on infolists for rendered output.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic markdown editor

Multi-line markdown source.

```python
MarkdownEditor.make('readme')
    .label('README')
    .rows(5)
```

![Orbit Basic markdown editor (light)](/examples/light/forms/markdown-editor/basic.png)

![Orbit Basic markdown editor (dark)](/examples/dark/forms/markdown-editor/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
