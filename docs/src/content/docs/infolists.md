---
title: Infolists
description: Read-only record views with typed entries — text, badges, images, code, and more.
---

**Infolists** are the “show” side of a resource — a definition list of entries over a record.

```python
from almasix.orbit.infolists import (
    Infolist, TextEntry, ImageEntry, CodeEntry, KeyValueEntry, RepeatableEntry,
)

infolist = Infolist.make("post").schema([
    TextEntry.make("title").badge().color("success"),
    TextEntry.make("slug").copyable(),
    TextEntry.make("body").prose().markdown(),
    ImageEntry.make("cover"),
    CodeEntry.make("payload"),
    KeyValueEntry.make("meta"),
    RepeatableEntry.make("tags").schema([
        TextEntry.make("name"),
    ]),
])

html = infolist.render(post)
```

Markup is a `<dl class="or-infolist">` — semantic, styleable, no surprise div soup.

## Entry API

```python
TextEntry.make("email")
    .label("Email")
    .format_state_using(lambda v: v.lower())
    .url("mailto:{state}")
    .copyable()
    .badge()
    .color("info")
    .icon("heroicon-o-envelope")
    .date_time()
    .markdown()
    .prose()
```

| Entry | Role |
|-------|------|
| `TextEntry` | Default |
| `IconEntry` | Icon-forward |
| `ImageEntry` | Image |
| `ColorEntry` | Color swatch |
| `CodeEntry` | Monospace / code block |
| `KeyValueEntry` | Dict-ish display |
| `RepeatableEntry` | Nested entry schema |

## On a resource

```python
@classmethod
def infolist(cls, infolist: Infolist) -> Infolist:
    return infolist.schema([
        TextEntry.make("title"),
        TextEntry.make("status").badge(),
    ])
```

Then `PostResource.get_infolist().render(record)` on your view page.
