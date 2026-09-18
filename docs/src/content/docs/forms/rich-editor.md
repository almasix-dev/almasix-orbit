---
title: Rich editor
description: RichEditor provides a TipTap-backed WYSIWYG surface with a configurable toolbar.
---

## Introduction

RichEditor provides a TipTap-backed WYSIWYG surface with a configurable toolbar. Content dehydrates as HTML in a hidden input bound with wire:model.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic rich editor

![Orbit Basic rich editor (light)](/examples/light/forms/rich-editor/basic.png)

![Orbit Basic rich editor (dark)](/examples/dark/forms/rich-editor/basic.png)

Bold, italic, link, and heading tools.

```python
RichEditor.make('body').label('Body').toolbar_buttons(['bold', 'italic', 'link', 'heading'])
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
