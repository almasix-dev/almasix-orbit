---
title: Rich editor
description: RichEditor provides a TipTap-backed WYSIWYG surface with a configurable toolbar.
---

## Introduction

RichEditor provides a TipTap-backed WYSIWYG surface with a configurable toolbar. Content dehydrates as HTML in a hidden input bound with wire:model.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic rich editor

Bold, italic, link, and heading tools.

```python
RichEditor.make('body')
    .label('Body')
    .toolbar_buttons(['bold', 'italic', 'link', 'heading'])
```

![Orbit Basic rich editor (light)](/examples/light/forms/rich-editor/basic.png)

![Orbit Basic rich editor (dark)](/examples/dark/forms/rich-editor/basic.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
