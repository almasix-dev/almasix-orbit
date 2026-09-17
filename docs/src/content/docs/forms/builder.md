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

![Orbit form example (light)](/examples/light/forms/overview.png)

![Orbit form example (dark)](/examples/dark/forms/overview.png)

