---
title: RichEditor
description: Orbit RichEditor — Textarea subclass with rich-editor classes and toolbar.
---

A textarea with light toolbar chrome — B / I / Link today, opinions tomorrow.

## Standalone

```python
from almasix.orbit.forms import Form, RichEditor

form = Form.make("demo").schema([
        RichEditor.make("body").label("Body").rows(12)
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
            RichEditor.make("content").rows(16).required(),
            RichEditor.make("bio").helper_text("Keep it short"),
        ])
```

## Key methods

- `Inherits Textarea (`.rows`, `.live`, …)`
- `Renders `or-editor or-editor-rich` plus a decorative toolbar`
- `.required() / .disabled(...) / .visible(...)`
- `.default(...) for HTML-ish content`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-RichEditor" data-field="body">
  <div class="or-editor-toolbar" aria-hidden="true"><span>B</span><span>I</span><span>Link</span></div>
  <label class="or-label" for="or-body">Body</label>
  <textarea class="or-textarea or-editor or-editor-rich" id="or-body" name="body" rows="12" wire:model="body">Hello <strong>Orbit</strong></textarea>
</div>
```
