---
title: Textarea
description: Textarea captures multi-line plain text — bios, notes, and markdown source.
---

## Introduction

Textarea captures multi-line plain text — bios, notes, and markdown source. Control height with rows or cols; autosize grows with content. MarkdownEditor and RichEditor extend Textarea for formatted content.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic textarea

![Orbit Basic textarea (light)](/examples/light/forms/textarea/basic.png)

![Orbit Basic textarea (dark)](/examples/dark/forms/textarea/basic.png)

Default multi-line field with placeholder and helper.

```python
Textarea.make('bio').label('Bio').placeholder('Tell us about yourself…').helper_text('Brief summary.')
```

## Custom rows

![Orbit Custom rows (light)](/examples/light/forms/textarea/rows.png)

![Orbit Custom rows (dark)](/examples/dark/forms/textarea/rows.png)

Explicit row count for taller editing surfaces.

```python
Textarea.make('notes').label('Notes').rows(6)
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
