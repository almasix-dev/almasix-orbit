---
title: FileUpload
description: Orbit FileUpload with accept types and max size hints.
---

Attach a file — covers, avatars, CSVs that somehow always arrive on Friday.

## Standalone

```python
from almasix.orbit.forms import Form, FileUpload

form = Form.make("demo").schema([
        FileUpload.make("cover")
            .accepted_file_types(["image/png", "image/jpeg"])
            .max_size(2048)  # KB
])
```

## In a Resource

```python
from almasix.orbit import Resource
from almasix.orbit.forms import Form, FileUpload

class PostResource(Resource):
    @classmethod
    def form(cls, form: Form) -> Form:
        return form.schema([
            FileUpload.make("avatar")
                .accepted_file_types(["image/*"])
                .max_size(512),
            FileUpload.make("attachment").label("Attachment"),
        ])
```

## Key methods

- `.accepted_file_types([...]) → `accept` attribute`
- `.max_size(kilobytes) — stored for validation/UI hints`
- `.required() / .disabled(...) / .visible(...)`
- `.label(...) / .helper_text(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-FileUpload" data-field="cover">
  <label class="or-label" for="or-cover">Cover</label>
  <input class="or-file" id="or-cover" type="file" name="cover"
         accept="image/png,image/jpeg" wire:model="cover" />
</div>
```
