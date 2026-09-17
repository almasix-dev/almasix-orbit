---
title: Builder
description: Orbit Builder — block picker with Block.make().label().icon().schema().
---

A Repeater with a block picker — compose pages from typed chunks.

## Standalone

```python
from almasix.orbit.forms import Form, Builder, Block, TextInput, Textarea

form = Form.make("demo").schema([
        Builder.make("blocks").blocks([
            Block.make("hero").label("Hero").icon("sparkles").schema([
                TextInput.make("heading").required(),
            ]).max_items(1),
            Block.make("quote").label("Quote").schema([
                Textarea.make("body").rows(3),
            ]),
        ])
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, Builder, Block, TextInput, Select

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            Builder.make("sections").blocks([
                Block.make("text").label("Text").schema([
                    TextInput.make("title").required(),
                ]),
                Block.make("gallery").label("Gallery").max_items(3).schema([
                    Select.make("layout").options({"grid": "Grid", "row": "Row"}),
                ]),
            ]),
        ])
```

## Key methods

- `.blocks([Block.make(...), …])` — typed schemas; picker replaces plain “Add item”
- `Block.make(name).label(...).icon(...).schema([...]).max_items(n)`
- Inherits Repeater: `.cloneable()`, `.collapsible()`, `.reorderable()`, `.min_items` / `.max_items`
- Wire: `addBuilderBlock(name, block)` when a picker button is clicked

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-Builder" data-field="blocks">
  <span class="or-label">Blocks</span>
  <div class="or-repeater">…</div>
  <div class="or-builder-picker" role="group">
    <button type="button" data-block="hero" data-max-items="1" wire:click="addBuilderBlock('blocks', 'hero')">Hero</button>
    <button type="button" data-block="quote" wire:click="addBuilderBlock('blocks', 'quote')">Quote</button>
  </div>
</div>
```
