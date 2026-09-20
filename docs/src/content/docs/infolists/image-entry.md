---
title: Image entry
description: ImageEntry renders covers and avatars — circular, square, sized, stacked with overflow counts, rings, and alt text.
---

## Introduction

`ImageEntry` displays one URL or a stack of images from list state — avatars, covers, and team stacks on a record view. Empty state uses `.placeholder(...)` or `.default_image_url(...)`; placeholders never become `<img>` tags.

Like other entries, the label stacks above the image by default so covers and avatars read as labeled fields on the detail sheet. Reach for `.circular()` / `.stacked()` when the layout should match social-style avatars rather than a rectangular cover.

## Basic image

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.infolists import ImageEntry

ImageEntry.make("photo").label("Cover").width(96).height(96).alt("Cover")
```

![Orbit Image entry basic (light)](/examples/light/infolists/image-entry/basic.png)

![Orbit Image entry basic (dark)](/examples/dark/infolists/image-entry/basic.png)

## Circular and square

`.circular()` rounds the image; `.square()` forces a square crop (clears circular).

```python title="app/orbit/resources/post_resource.py"
ImageEntry.make("photo").label("Avatar").circular().size(56).alt("Avatar")
```

![Orbit Image entry circular (light)](/examples/light/infolists/image-entry/circular.png)

![Orbit Image entry circular (dark)](/examples/dark/infolists/image-entry/circular.png)

## Size helpers

| Method | Notes |
|--------|-------|
| `.size(56)` / `.image_size(56)` | Pixel square, or named size class |
| `.width` / `.height` | Independent dimensions |
| `.ring(2)` | Avatar ring width |
| `.overlap(10)` | Stack overlap (stacked mode) |

## Stacked images

When state is a list of URLs, `.stacked()` overlaps them. `.limit(n)` caps how many are shown and renders `+N` for the overflow.

```python title="app/orbit/resources/post_resource.py"
ImageEntry.make("photos")
    .label("Team")
    .stacked()
    .circular()
    .limit(2)
    .overlap(10)
    .ring(2)
    .size(40)
```

![Orbit Image entry stacked (light)](/examples/light/infolists/image-entry/stacked.png)

![Orbit Image entry stacked (dark)](/examples/dark/infolists/image-entry/stacked.png)

## Defaults, alt, and extra attributes

```python title="app/orbit/resources/post_resource.py"
ImageEntry.make("photo")
    .default_image_url("/images/fallback.png")
    .alt(lambda record, **_: record.get("title", "Image"))
    .extra_img_attributes({"loading": "lazy"})
```

## API cheat sheet

| Method | Notes |
|--------|-------|
| `.circular` / `.square` | Shape |
| `.size` / `.image_size` / `.width` / `.height` | Dimensions |
| `.stacked` / `.limit` / `.overlap` / `.ring` | Stack layout |
| `.default_image_url` | Fallback URL when empty |
| `.alt` / `.extra_img_attributes` | Accessibility + img attrs |
| `.placeholder` | Text when empty (no default image) |
