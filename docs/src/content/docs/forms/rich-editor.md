---
title: Rich editor
description: Orbit RichEditor — TipTap CDN surface with toolbar config and hidden HTML input.
---

A TipTap-backed editor: toolbar from config, HTML stored in a hidden input for Conduit.

## Standalone

```python
from almasix.orbit.forms import Form, RichEditor

form = Form.make("demo").schema([
        RichEditor.make("body")
            .label("Body")
            .toolbar_buttons(["bold", "italic", "link", "strike"])
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, RichEditor

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            RichEditor.make("content").toolbar_buttons(["bold", "italic", "link"]).required(),
            RichEditor.make("bio").helper_text("Keep it short"),
        ])
```

## Key methods

- `.toolbar_buttons([...])` → toolbar chrome + `data-toolbar` for TipTap init
- Renders `.or-editor-rich[data-tiptap]` plus a hidden `input` (`data-tiptap-input`) holding HTML
- Panel `orbit.js` loads TipTap from CDN and syncs `editor.getHTML()` into the hidden input
- `.required() / .disabled(...) / .visible(...)`
- `.default(...)` for initial HTML

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/forms/overview.png)

![Orbit form example (dark)](/examples/dark/forms/overview.png)

