---
title: Code editor
description: Orbit CodeEditor — Textarea subclass styled for code.
---

Monospace intentions — JSON payloads, snippets, config that shouldn’t look like prose.

## Standalone

```python
from almasix.orbit.forms import Form, CodeEditor

form = Form.make("demo").schema([
        CodeEditor.make("payload").label("JSON").rows(10)
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, CodeEditor

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            CodeEditor.make("script").rows(16),
            CodeEditor.make("config").helper_text("YAML or JSON"),
        ])
```

## Key methods

- `Inherits Textarea`
- `Adds `or-editor or-editor-code``
- `.rows(n) / .required() / .readonly()`
- `.default("{}")`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).


## Preview

![Orbit forms/rich-editor (light)](/examples/light/forms/rich-editor.png)

![Orbit forms/rich-editor (dark)](/examples/dark/forms/rich-editor.png)
