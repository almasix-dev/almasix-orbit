---
title: MarkdownEditor
description: Orbit MarkdownEditor — Textarea subclass with markdown editor classes.
---

Markdown in a textarea — for people who type `**bold**` for fun.

## Standalone

```python
from almasix.orbit.forms import Form, MarkdownEditor

form = Form.make("demo").schema([
        MarkdownEditor.make("readme").label("README").rows(14)
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, MarkdownEditor

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            MarkdownEditor.make("body").rows(20).required(),
            MarkdownEditor.make("changelog"),
        ])
```

## Key methods

- `Inherits Textarea`
- `Adds `or-editor or-editor-markdown``
- `.rows(n) / .required() / .disabled(...)`
- `.default("# Title\n")`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/form.png)

![Orbit form example (dark)](/examples/dark/form.png)

