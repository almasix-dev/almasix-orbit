---
title: Image column
description: ImageColumn — circular avatars, stacked faces, sizes, and default image URLs.
---

`ImageColumn` renders a URL (or list of URLs) as an image or avatar. Use `.circular()` for round masks, `.stacked()` for multiple images, and `.default_image_url()` when the value is missing.

## Standalone example

```python
from almasix.orbit.tables import Table, TextColumn, ImageColumn

table = (
    Table.make("people")
    .columns([
        ImageColumn.make("avatar_url")
            .circular()
            .size(40)
            .default_image_url("/images/avatar-fallback.png"),
        TextColumn.make("name").searchable().sortable(),
        ImageColumn.make("gallery_urls").stacked().limit(3).circular().size(28),
    ])
    .records([
        {
            "id": 1,
            "name": "Ada",
            "avatar_url": "/avatars/ada.png",
            "gallery_urls": ["/a.png", "/b.png", "/c.png", "/d.png"],
        },
        {"id": 2, "name": "No Photo", "avatar_url": None, "gallery_urls": []},
    ])
)
```

A list state with `.stacked()` overlaps images; `.limit(n)` caps how many show before a `+N` chip.

## In a Resource example

```python
from almasix.orbit import Resource
from almasix.orbit.tables import Table, ImageColumn, TextColumn

class UserResource(Resource):
    @classmethod
    def table(cls, table: Table) -> Table:
        return table.columns([
            ImageColumn.make("avatar")
                .label("")
                .circular()
                .size("md")
                .default_image_url("/vendor/orbit/avatar.svg"),
            TextColumn.make("name").searchable().sortable().weight("bold"),
            TextColumn.make("email").copyable(),
        ])
```

### Size notes

- Integer (or digit string) → inline `width` / `height` in px
- Named token (`sm`, `md`, `lg`) → `or-avatar-*` CSS class

```python
ImageColumn.make("photo").size(48)       # 48×48 px
ImageColumn.make("photo").size("lg")     # class-based
ImageColumn.make("photo").circular()     # round mask
```

## Key methods

- `.circular(condition=True)` — round avatar
- `.size(str | int)` — pixels or size token
- `.default_image_url(url)` — fallback when state is empty
- `.stacked(condition=True)` — overlap multiple URLs
- `.limit(count)` — max faces in a stack (then `+N`)
- `.align_center()` / `.toggleable(...)`

## Preview

![Image column (light)](/examples/light/tables/image-color.png)
![Image column (dark)](/examples/dark/tables/image-color.png)
