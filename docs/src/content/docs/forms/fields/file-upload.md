---
title: FileUpload
description: Orbit FileUpload with disk, avatar, previews, and accept helpers.
---

Attach a file — covers, avatars, CSVs that somehow always arrive on Friday.

## Standalone

```python
from almasix.orbit.forms import Form, FileUpload

form = Form.make("demo").schema([
        FileUpload.make("cover")
            .disk("public")
            .directory("covers")
            .accepted_file_types(["image/png", "image/jpeg"])
            .image_preview()
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
            FileUpload.make("avatar").avatar().disk("s3").directory("avatars"),
            FileUpload.make("gallery").image().multiple().reorderable(),
            FileUpload.make("attachment").label("Attachment"),
        ])
```

## Key methods

- `.disk(name)` / `.directory(path)` → `data-disk` / `data-directory`
- `.multiple()` / `.avatar()` / `.image_preview()` / `.reorderable()`
- `.image()` / `.accepted_images()` — common image MIME set + preview
- `.accepted_file_types([...])` → `accept` attribute
- `.max_size` / `.min_size` (KB) and `.image_size(min_width=…, …)` for host validation hints
- `.required() / .disabled(...) / .visible(...)`
- `.label(...) / .helper_text(...)`

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` — see [Form closures](/forms/closures/).

## Preview

```html
<div class="or-field or-field-FileUpload or-file-avatar" data-field="avatar"
     data-disk="s3" data-directory="avatars" data-avatar="true" data-image-preview="true">
  <label class="or-label" for="or-avatar">Avatar</label>
  <div class="or-file-preview" data-preview-grid></div>
  <input class="or-file" id="or-avatar" type="file" name="avatar" accept="image/*" wire:model="avatar" />
</div>
```
