---
title: Builder
description: Builder extends Repeater with typed Block definitions and a block picker instead of a generic Add button.
---

## Introduction

`Builder` is a `Repeater` whose items carry a `type` (or `block`) key. Define blocks with `Block.make(...).label().icon().schema([...]).max_items(n)`, then pass them to `.blocks([...])`. The Add button is replaced by a picker that calls `addBuilderBlock`. Each item renders the schema for its matching block type. Use Builder for page builders, email layouts, and CMS section stacks.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic builder

Register at least one block. Empty state still seeds repeater defaults; the picker adds typed rows.

```python title="app/orbit/resources/example_resource.py"
from almasix.orbit.forms import Block, Builder, TextInput, Textarea

Builder.make('content')
    .label('Page blocks')
    .blocks([
        Block.make('hero')
            .label('Hero')
            .schema([
                TextInput.make('heading').label('Heading').required(),
                Textarea.make('subheading').label('Subheading'),
            ]),
        Block.make('rich_text')
            .label('Rich text')
            .schema([Textarea.make('body').label('Body')]),
    ])
```

![Orbit Basic builder (light)](/examples/light/forms/builder/basic.png)

![Orbit Basic builder (dark)](/examples/dark/forms/builder/basic.png)

## Block icons and max items

`.icon()` sets `data-icon` on the picker button. `.max_items()` on a `Block` disables that picker option once the count of that type reaches the limit.

```python title="app/orbit/resources/example_resource.py"
Builder.make('content')
    .label('Content')
    .blocks([
        Block.make('cta')
            .label('Call to action')
            .icon('heroicon-o-link')
            .max_items(1)
            .schema([TextInput.make('label'), TextInput.make('url').url()]),
        Block.make('quote')
            .label('Quote')
            .icon('heroicon-o-chat-bubble-left-right')
            .schema([Textarea.make('text')]),
    ])
```

![Orbit Block icons and max items (light)](/examples/light/forms/builder/block-limits.png)

![Orbit Block icons and max items (dark)](/examples/dark/forms/builder/block-limits.png)

## Block picker columns

`.block_picker_columns(n)` styles the picker as a CSS grid with `n` columns for denser block catalogs.

```python title="app/orbit/resources/example_resource.py"
Builder.make('sections')
    .label('Sections')
    .block_picker_columns(3)
    .blocks([
        Block.make('hero').label('Hero').schema([TextInput.make('title')]),
        Block.make('gallery').label('Gallery').schema([TextInput.make('caption')]),
        Block.make('faq').label('FAQ').schema([TextInput.make('question')]),
    ])
```

![Orbit Block picker columns (light)](/examples/light/forms/builder/picker-columns.png)

![Orbit Block picker columns (dark)](/examples/dark/forms/builder/picker-columns.png)

## Shared repeater controls

Because Builder extends Repeater, `.cloneable()`, `.reorderable()`, `.collapsible()`, `.item_label()`, and item limits all apply to typed blocks.

```python title="app/orbit/resources/example_resource.py"
Builder.make('content')
    .label('Content')
    .cloneable()
    .reorderable()
    .blocks([
        Block.make('hero').label('Hero').schema([TextInput.make('heading')]),
    ])
```

![Orbit Shared repeater controls (light)](/examples/light/forms/builder/reorderable.png)

![Orbit Shared repeater controls (dark)](/examples/dark/forms/builder/reorderable.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, `.required()`, and repeater `.item_label()` where applicable — see [Form closures](/forms/closures/).
