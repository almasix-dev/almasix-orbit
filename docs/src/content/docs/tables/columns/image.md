---
title: Image column
description: ImageColumn — circular or square avatars, sizes, stacked galleries, rings, overlap, alt text, and default images.
---

## Introduction

`ImageColumn` renders a URL (or list of URLs) from the record as an `<img>`. Reach for it when a row needs an avatar, logo, cover thumbnail, or a small gallery of faces:

```python
from almasix.orbit.tables import ImageColumn

ImageColumn.make("avatar_url")
```

## Managing the image shape

Images render as squares by default. Use `.circular()` for an avatar-style round mask:

```python
ImageColumn.make("avatar_url").circular()
```

`.square()` is available to be explicit, or to switch a column back after conditionally applying `.circular()`.

## Managing the image size

Set a fixed size in pixels, or a size token (`sm`, `md`, `lg`, …) that maps to a CSS class:

```python
ImageColumn.make("avatar_url").size(40)
ImageColumn.make("avatar_url").size("lg")
```

If width and height need to differ, use `.image_width()` and `.image_height()` instead — each accepts a pixel number or any CSS length:

```python
ImageColumn.make("banner_url").image_width(120).image_height("3rem")
```

## Adding a default image URL

When the state is empty, `.default_image_url()` renders a fallback image instead of leaving the cell blank:

```python
ImageColumn.make("avatar_url").default_image_url("/images/avatar-fallback.png")
```

## Stacking images

If the column's state is a list of URLs, `.stacked()` overlaps them into a compact group — handy for “team members on this project” or similar galleries:

```python
ImageColumn.make("team_avatars").stacked().circular().size(28)
```

### Limiting the number of images shown

Use `.limit()` to cap how many images render before the rest collapse into a `+N` chip:

```python
ImageColumn.make("team_avatars").stacked().limit(3)
```

### Customizing the ring and overlap

`.ring()` sets the border width shown around each avatar (useful with `.stacked()` so avatars separate from one another visually), and `.overlap()` controls how tightly stacked avatars sit on top of each other:

```python
ImageColumn.make("team_avatars")
    .stacked()
    .limit(3)
    .ring(2)
    .overlap("0.6rem")
```

## Adding alt text

Set accessible `alt` text for the rendered `<img>` tags — pass a string, or a callback for per-record text:

```python
ImageColumn.make("avatar_url").alt(
    lambda record=None, **_: f"{record.get('name', 'User')}'s avatar",
)
```

## Adding extra image attributes

`.extra_img_attributes()` merges arbitrary HTML attributes onto the rendered `<img>` tag — handy for `loading="lazy"` or `data-*` hooks:

```python
ImageColumn.make("avatar_url").extra_img_attributes({"loading": "lazy"})
```

## Full example

```python
from almasix.orbit.tables import Table, TextColumn, ImageColumn

Table.make("team").columns([
    ImageColumn.make("avatar_url")
        .circular()
        .size(40)
        .ring(2)
        .alt(lambda record=None, **_: record.get("name", ""))
        .default_image_url("/images/avatar-fallback.png"),
    TextColumn.make("name").searchable().sortable().weight("bold"),
    ImageColumn.make("teammate_urls")
        .stacked()
        .limit(3)
        .circular()
        .size(28)
        .overlap("0.6rem"),
]).records([
    {
        "id": 1,
        "name": "Ada Lovelace",
        "avatar_url": "https://api.dicebear.com/9.x/shapes/svg?seed=ada",
        "teammate_urls": [
            "https://api.dicebear.com/9.x/shapes/svg?seed=a",
            "https://api.dicebear.com/9.x/shapes/svg?seed=b",
            "https://api.dicebear.com/9.x/shapes/svg?seed=c",
            "https://api.dicebear.com/9.x/shapes/svg?seed=d",
        ],
    },
    {"id": 2, "name": "No Photo", "avatar_url": None, "teammate_urls": []},
])
```

## Key methods

| Method | Effect |
|--------|--------|
| `.circular(condition=True)` / `.square(condition=True)` | Avatar shape |
| `.size(str \| int)` | Pixel size or size token |
| `.image_width(value)` / `.image_height(value)` | Independent width / height |
| `.default_image_url(url)` | Fallback when state is empty |
| `.stacked(condition=True)` / `.limit(count)` | Overlapping galleries |
| `.ring(width)` / `.overlap(amount)` | Stack spacing |
| `.alt(str \| callable)` | Accessible `alt` text |
| `.extra_img_attributes(dict)` | Arbitrary `<img>` attributes |
| `.align_center()` / `.toggleable(...)` | Inherited [shared helpers](/tables/columns/overview/) |

## Preview

![Image column (light)](/examples/light/tables/image-color.png)
![Image column (dark)](/examples/dark/tables/image-color.png)

![Stacked images (light)](/examples/light/tables/image-stacked.png)
![Stacked images (dark)](/examples/dark/tables/image-stacked.png)
