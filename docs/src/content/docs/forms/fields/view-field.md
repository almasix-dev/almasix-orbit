---
title: ViewField
description: Orbit ViewField — custom HTML content field that skips dehydration.
---

Custom HTML inside the form — not dehydrated, fully yours.

## Standalone

```python
from almasix.orbit.forms import Form, ViewField

form = Form.make("demo").schema([
        ViewField.make("preview")
            .content("<strong class=\"or-badge\">Live preview</strong>")
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, ViewField

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            ViewField.make("summary")
                .content(lambda state=None, record=None, **_: f"<p>{record.get('title')}</p>")
                .label("Summary"),
        ])
```

## Key methods

- `.content(str | callable) — HTML string (callable gets `state` + ctx)`
- `Not dehydrated by default`
- `.label(...) / .visible(...)`
- `Falls back to escaped state when content is unset`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/form.png)

![Orbit form example (dark)](/examples/dark/form.png)

