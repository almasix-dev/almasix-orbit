---
title: Rich editor
description: RichEditor provides TipTap-oriented toolbar chrome over a contenteditable surface bound to a hidden input.
---

## Introduction

`RichEditor` subclasses `Textarea` but renders a toolbar of tool buttons, a `data-tiptap` editor surface, and a hidden input that carries HTML/state via `wire:model` (or live binding when `.live()` is set). Default toolbar buttons are `bold`, `italic`, and `link`. Customize with `.toolbar_buttons([...])`. Actual TipTap bootstrapping lives in panel assets — Python owns the fluent config and markup shell.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic rich editor

A labeled rich text field for post bodies, product descriptions, and email templates. The hidden input holds the dehydrated HTML string.

```python title="app/orbit/resources/example_resource.py"
RichEditor.make('body')
    .label('Body')
    .helper_text('Supports basic formatting.')
```

![Orbit Basic rich editor (light)](/examples/light/forms/rich-editor/basic.png)

![Orbit Basic rich editor (dark)](/examples/dark/forms/rich-editor/basic.png)

## Custom toolbar

`.toolbar_buttons()` replaces the default tool list. Each entry becomes a toolbar button with `data-tool="{name}"` and a short label. Stick to tools your Alpine/TipTap bridge implements.

```python title="app/orbit/resources/example_resource.py"
RichEditor.make('content')
    .label('Content')
    .toolbar_buttons(['bold', 'italic', 'link', 'heading', 'bulletList'])
```

![Orbit Custom toolbar (light)](/examples/light/forms/rich-editor/toolbar.png)

![Orbit Custom toolbar (dark)](/examples/dark/forms/rich-editor/toolbar.png)

## Live updates

`.live()` switches the hidden input to `wire:model.live` so sibling fields and visibility closures can react as the user types. Use sparingly on large documents.

```python title="app/orbit/resources/example_resource.py"
RichEditor.make('summary')
    .label('Summary')
    .live()
    .toolbar_buttons(['bold', 'italic'])
```

![Orbit Live updates (light)](/examples/light/forms/rich-editor/live.png)

![Orbit Live updates (dark)](/examples/dark/forms/rich-editor/live.png)

## Disabled and readonly

`.disabled()` / `.readonly()` propagate to the editor surface attribute so hosts can lock editing while still showing content.

```python title="app/orbit/resources/example_resource.py"
RichEditor.make('terms')
    .label('Terms')
    .disabled()
```

![Orbit Disabled and readonly (light)](/examples/light/forms/rich-editor/disabled.png)

![Orbit Disabled and readonly (dark)](/examples/dark/forms/rich-editor/disabled.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
