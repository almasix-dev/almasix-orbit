---
title: File upload
description: FileUpload handles single or multiple files with image preview, avatar cropping layout, and accepted MIME filters.
---

## Introduction

FileUpload handles single or multiple files with image preview, avatar cropping layout, and accepted MIME filters. Image and avatar presets configure accept lists and preview grids automatically.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Basic file upload

![Orbit Basic file upload (light)](/examples/light/forms/file-upload/basic.png)

![Orbit Basic file upload (dark)](/examples/dark/forms/file-upload/basic.png)

Generic attachment picker.

```python
FileUpload.make('attachment').label('Attachment')
```

## Image upload

![Orbit Image upload (light)](/examples/light/forms/file-upload/image.png)

![Orbit Image upload (dark)](/examples/dark/forms/file-upload/image.png)

Image MIME types with preview.

```python
FileUpload.make('cover').image().label('Cover image')
```

## Avatar upload

![Orbit Avatar upload (light)](/examples/light/forms/file-upload/avatar.png)

![Orbit Avatar upload (dark)](/examples/dark/forms/file-upload/avatar.png)

Circular avatar preset with image/* accept.

```python
FileUpload.make('avatar').avatar().label('Avatar')
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
