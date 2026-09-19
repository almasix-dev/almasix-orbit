---
title: Prime components
description: Read-only Text, Icon, Image, and UnorderedList primes for infolists and inline form summaries.
---

## Introduction

Primes are read-only display components — text (optionally badge / markdown / HTML), icons, images, and lists. Use them in infolists, empty-state bodies, or beside form fields when you need chrome without editable state.

```python title="app/orbit/schemas/primes_demo.py"
from almasix.orbit.schemas import Text, Icon, Image, UnorderedList

Text.make().content("Published").badge().color("success")
Icon.make().icon("heroicon-o-check").color("success").size("lg")
Image.make().src("/avatars/a.png").image_size(48).align_center()
UnorderedList.make().items(["Tables", "Forms", "Panels"]).bullet_size("sm")
```

![Primes (light)](/examples/light/schemas/primes-all.png)
![Primes (dark)](/examples/dark/schemas/primes-all.png)

## Text

`Text` renders inline or block copy. Pass a string or a callable to `.content(...)`; without content it stringifies the render `state`.

```python title="app/orbit/schemas/text_prime.py"
from almasix.orbit.schemas import Text

Text.make()
    .content("Published")
    .badge()
    .color("success")
```

![Text prime (light)](/examples/light/schemas/primes/text.png)
![Text prime (dark)](/examples/dark/schemas/primes/text.png)

### Formatting

```python title="app/orbit/schemas/text_formatting.py"
Text.make().content("**Bold** and `code`").markdown()
Text.make().content("<em>Trusted</em> HTML").html()
Text.make().content("SKU-104").size("sm").weight("semibold")
Text.make().content("Monospace").font_family("ui-monospace, monospace")
Text.make().content("Hover me").tooltip("Copied from inventory")
Text.make().content("Verified").icon("heroicon-o-check-badge").color("success")
```

| Method | Role |
|--------|------|
| `.content` | Static string or callable (`state`, `record`, …) |
| `.markdown` | Light markdown → HTML (`**`, `*`, `` ` ``) |
| `.html` | Pass content through unescaped (trusted HTML only) |
| `.badge` | Pill / badge chrome |
| `.color` | Inbuilt color name or callable |
| `.size` | `xs` · `sm` · `md` · `lg` · `xl` |
| `.weight` | `light` · `normal` · `medium` · `semibold` · `bold` |
| `.font_family` | CSS `font-family` value |
| `.tooltip` | Native `title` tooltip |
| `.icon` | Icon before the text |

![Text variants (light)](/examples/light/schemas/primes-text.png)
![Text variants (dark)](/examples/dark/schemas/primes-text.png)

## Icon

```python title="app/orbit/schemas/icon_prime.py"
from almasix.orbit.schemas import Icon

Icon.make()
    .icon("heroicon-o-check")
    .color("success")
    .size("lg")
    .tooltip("Verified")
```

![Icon prime (light)](/examples/light/schemas/primes/icon.png)
![Icon prime (dark)](/examples/dark/schemas/primes/icon.png)

`.icon(...)` accepts a string or callable. Sizes match text primes (`xs`–`xl`).

| Method | Role |
|--------|------|
| `.icon` | Icon name or callable |
| `.color` | Color class |
| `.size` | `xs` · `sm` · `md` · `lg` · `xl` |
| `.tooltip` | Native `title` tooltip |

## Image

```python title="app/orbit/schemas/image_prime.py"
from almasix.orbit.schemas import Image

Image.make()
    .src("https://api.dicebear.com/9.x/shapes/svg?seed=orbit")
    .image_size(48)
    .align_center()
    .tooltip("Avatar")
```

![Image prime (light)](/examples/light/schemas/primes/image.png)
![Image prime (dark)](/examples/dark/schemas/primes/image.png)

`.src(...)` may be a URL string or callable. Prefer `.image_size` when width and height should match; otherwise set `.width` / `.height` independently.

### Alignment

```python title="app/orbit/schemas/image_align.py"
Image.make().src(url).align_start()
Image.make().src(url).align_center()
Image.make().src(url).align_end()
# or: .alignment("start" | "center" | "end")
```

| Method | Role |
|--------|------|
| `.src` | Image URL or callable |
| `.image_size` | Square size (px int or CSS length) |
| `.width` / `.height` | Independent dimensions |
| `.align_start` / `.align_center` / `.align_end` | Horizontal alignment helpers |
| `.alignment` | `"start"` · `"center"` · `"end"` |
| `.tooltip` | Native `title` on the `<img>` |

## Unordered list

```python title="app/orbit/schemas/list_prime.py"
from almasix.orbit.schemas import UnorderedList, Text

UnorderedList.make()
    .items(["Tables", "Forms", "Panels"])
    .bullet_size("sm")

# Items may be strings, nested components, or a callable:
UnorderedList.make().items([
    Text.make().content("Nested prime").badge(),
    "Plain string",
])
```

![List prime (light)](/examples/light/schemas/primes/list.png)
![List prime (dark)](/examples/dark/schemas/primes/list.png)

| Method | Role |
|--------|------|
| `.items` | Sequence of strings / components, or callable |
| `.bullet_size` | `xs` · `sm` · `md` · `lg` · `xl` |
