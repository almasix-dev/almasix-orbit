---
title: File upload
description: FileUpload wraps a native file input with disk, preview, avatar, size, and image-editor configuration attributes.
---

## Introduction

`FileUpload` renders `<input type="file">` inside Orbit field chrome. Most storage and preview options are fluent setters that emit `data-*` attributes for the Conduit host / Alpine assets — the Python package does not upload to S3 by itself. Multiple selection is enabled when `.multiple()` is set or `.max_files()` is greater than 1. Image and avatar presets configure MIME accept lists and preview grids for you.

Each variation below includes a detailed explanation, the fluent API to paste into your schema, and light/dark screenshots of the rendered control.

## Basic file upload

A generic attachment field with no accept filter. Users can pick any file the browser allows. Add `.helper_text()` for size or type guidance until you tighten `.accepted_file_types()`.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('attachment')
    .label('Attachment')
    .helper_text('PDF or Office documents preferred.')
```

![Orbit Basic file upload (light)](/examples/light/forms/file-upload/basic.png)

![Orbit Basic file upload (dark)](/examples/dark/forms/file-upload/basic.png)

## Image upload

`.image()` (alias `.accepted_images()`) sets accept to common image MIME types and turns on image preview (`data-image-preview`). Use for covers, galleries, and media that should show a thumbnail grid after selection.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('cover')
    .image()
    .label('Cover image')
```

![Orbit Image upload (light)](/examples/light/forms/file-upload/image.png)

![Orbit Image upload (dark)](/examples/dark/forms/file-upload/image.png)

## Avatar upload

`.avatar()` enables circular avatar chrome (`or-file-avatar`), forces image preview, and defaults accept to `image/*` when no types were set. Ideal for profile photos.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('avatar')
    .avatar()
    .label('Avatar')
```

![Orbit Avatar upload (light)](/examples/light/forms/file-upload/avatar.png)

![Orbit Avatar upload (dark)](/examples/dark/forms/file-upload/avatar.png)

## Accepted file types

`.accepted_file_types([...])` joins MIME or extension tokens into the HTML `accept` attribute. Prefer explicit lists when you need PDFs only or mixed documents without enabling image preview.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('contract')
    .label('Contract')
    .accepted_file_types(['application/pdf', '.docx'])
```

![Orbit Accepted file types (light)](/examples/light/forms/file-upload/accepted-types.png)

![Orbit Accepted file types (dark)](/examples/dark/forms/file-upload/accepted-types.png)

## Disk, directory, and visibility

`.disk()`, `.directory()`, and `.visibility()` emit `data-disk`, `data-directory`, and `data-visibility` for the storage driver your host wires up (for example public vs private disks). They do not change the browser input by themselves.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('logo')
    .image()
    .label('Logo')
    .disk('s3')
    .directory('brands')
    .visibility('public')
```

![Orbit Disk, directory, and visibility (light)](/examples/light/forms/file-upload/disk.png)

![Orbit Disk, directory, and visibility (dark)](/examples/dark/forms/file-upload/disk.png)

## Size limits

`.max_size()` / `.min_size()` take kilobytes and emit `data-max-size` / `data-min-size` for client and host validation. Field-level `.max_size()` is the same helper used across uploads.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('resume')
    .label('Resume')
    .accepted_file_types(['application/pdf'])
    .min_size(10)
    .max_size(2048)
```

![Orbit Size limits (light)](/examples/light/forms/file-upload/size-limits.png)

![Orbit Size limits (dark)](/examples/dark/forms/file-upload/size-limits.png)

## Image dimensions

`.image_size(min_width=…, max_width=…, min_height=…, max_height=…)` stores pixel bounds as `data-image-*` attributes for host-side checks after upload.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('banner')
    .image()
    .label('Banner')
    .image_size(min_width=1200, max_width=2400, min_height=400, max_height=800)
```

![Orbit Image dimensions (light)](/examples/light/forms/file-upload/image-size.png)

![Orbit Image dimensions (dark)](/examples/dark/forms/file-upload/image-size.png)

## Multiple files

`.multiple()` or `.max_files(n)` with `n > 1` adds the `multiple` attribute. `.min_files()` / `.max_files()` also emit data attributes for count validation in the host.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('gallery')
    .image()
    .label('Gallery')
    .multiple()
    .min_files(1)
    .max_files(8)
```

![Orbit Multiple files (light)](/examples/light/forms/file-upload/multiple.png)

![Orbit Multiple files (dark)](/examples/dark/forms/file-upload/multiple.png)

## Preview and file actions

Toggle preview grid and action affordances: `.image_preview()`, `.previewable()`, `.downloadable()`, `.openable()`, and `.reorderable()`. Preview markup is a live region (`or-file-preview`); actions are data flags for Alpine/host handlers.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('assets')
    .image()
    .label('Assets')
    .multiple()
    .image_preview()
    .downloadable()
    .openable()
    .reorderable()
```

![Orbit Preview and file actions (light)](/examples/light/forms/file-upload/preview-actions.png)

![Orbit Preview and file actions (dark)](/examples/dark/forms/file-upload/preview-actions.png)

## Panel layout and preview height

`.panel_layout()` switches to panel-oriented chrome via `data-panel-layout`. `.image_preview_height(px)` sets `data-preview-height` for thumbnail sizing.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('photos')
    .image()
    .label('Photos')
    .panel_layout()
    .image_preview_height(120)
```

![Orbit Panel layout and preview height (light)](/examples/light/forms/file-upload/panel-layout.png)

![Orbit Panel layout and preview height (dark)](/examples/dark/forms/file-upload/panel-layout.png)

## Storage behavior flags

Fluent flags for how the host should treat files after pick: `.store_files(False)` skips persistence, `.move_files()` moves instead of copy, `.preserve_filenames()` keeps original names, `.fetch_file_information(False)` skips metadata fetch, and `.prevent_file_path_tampering()` marks the field for path hardening.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('import')
    .label('Import file')
    .store_files(False)
    .preserve_filenames()
    .prevent_file_path_tampering()
```

![Orbit Storage behavior flags (light)](/examples/light/forms/file-upload/storage-flags.png)

![Orbit Storage behavior flags (dark)](/examples/dark/forms/file-upload/storage-flags.png)

## Image editor stub

`.image_editor()` and `.image_editor_aspect_ratios([...])` render a hidden `or-file-image-editor` region and data attributes (`data-image-editor`, `data-aspect-ratios`). This is chrome for a host-provided editor — not a full crop UI inside the forms package.

```python title="app/orbit/resources/example_resource.py"
FileUpload.make('hero')
    .image()
    .label('Hero')
    .image_editor_aspect_ratios(['1:1', '16:9'])
```

![Orbit Image editor stub (light)](/examples/light/forms/file-upload/image-editor.png)

![Orbit Image editor stub (dark)](/examples/dark/forms/file-upload/image-editor.png)

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
