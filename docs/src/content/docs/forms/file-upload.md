---
title: File upload
description: FileUpload handles single or multiple files with image preview, avatar cropping layout, and accepted MIME filters.
---

## Introduction

FileUpload handles single or multiple files with image preview, avatar cropping layout, and accepted MIME filters. Image and avatar presets configure accept lists and preview grids automatically.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Basic file upload

Generic attachment picker.

```python
FileUpload.make('attachment')
    .label('Attachment')
```

![Orbit Basic file upload (light)](/examples/light/forms/file-upload/basic.png)

![Orbit Basic file upload (dark)](/examples/dark/forms/file-upload/basic.png)

## Image upload

Image MIME types with preview.

```python
FileUpload.make('cover')
    .image()
    .label('Cover image')
```

![Orbit Image upload (light)](/examples/light/forms/file-upload/image.png)

![Orbit Image upload (dark)](/examples/dark/forms/file-upload/image.png)

## Avatar upload

Circular avatar preset with image/* accept.

```python
FileUpload.make('avatar')
    .avatar()
    .label('Avatar')
```

![Orbit Avatar upload (light)](/examples/light/forms/file-upload/avatar.png)

![Orbit Avatar upload (dark)](/examples/dark/forms/file-upload/avatar.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
