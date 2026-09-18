---
title: Markdown editor
description: MarkdownEditor styles a Textarea for markdown source editing.
---

## Introduction

MarkdownEditor styles a Textarea for markdown source editing. Pair with a preview prime on infolists for rendered output.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic markdown editor

![Orbit Basic markdown editor (light)](/examples/light/forms/markdown-editor/basic.png)

![Orbit Basic markdown editor (dark)](/examples/dark/forms/markdown-editor/basic.png)

Multi-line markdown source.

```python
(
    MarkdownEditor.make('readme')
    .label('README')
    .rows(5)
)
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
