---
title: RelationshipRepeater
description: Orbit RelationshipRepeater — Repeater subclass for related record lists.
---

Repeater aimed at related records — same nested schema, relationship-shaped intent.

## Standalone

```python
from almasix.orbit.forms import Form, RelationshipRepeater, TextInput, Textarea, Select

form = Form.make("demo").schema([
        RelationshipRepeater.make("comments").schema([
            TextInput.make("author").required(),
            Textarea.make("body").rows(3),
        ])
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, RelationshipRepeater, TextInput, Textarea, Select

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            RelationshipRepeater.make("items").schema([
                TextInput.make("sku").required(),
                TextInput.make("qty").integer().required(),
            ]),
        ])
```

## Key methods

- `.schema([...])`
- `.relationship(...) available via Field base when you wire titles`
- `CSS: `or-field-RelationshipRepeater``
- `.label(...) / .visible(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

![Orbit form example (light)](/examples/light/form.png)

![Orbit form example (dark)](/examples/dark/form.png)

