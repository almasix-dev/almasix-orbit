---
title: Tabs
description: Split a schema into horizontal panels — icons, badges, active tab, and optional persist.
---

## Introduction

`Tabs` splits a form or infolist into horizontal panels. Each tab owns its own nested schema. Icons and badges surface counts or status without leaving the page.

```python title="app/orbit/schemas/tabs_basic.py"
from almasix.orbit.schemas import Tabs
from almasix.orbit.forms import TextInput, Textarea

Tabs.make("main")
    .tabs(
        {"label": "General", "schema": [TextInput.make("title")]},
        {"label": "SEO", "schema": [Textarea.make("meta_description")]},
    )
    .active_tab(0)
```

![Basic tabs (light)](/examples/light/schemas/tabs/basic.png)
![Basic tabs (dark)](/examples/dark/schemas/tabs/basic.png)

## Defining tabs

Prefer a `Tab` for each panel. The tab owns its label, icon, badge, and schema, so each one can be styled on its own:

```python title="app/orbit/schemas/tabs_components.py"
from almasix.orbit.schemas import Tab, Tabs

Tabs.make("main").tabs(
    Tab.make("account").label("Account").icon("heroicon-o-user").schema([
        TextInput.make("email"),
    ]),
    Tab.make("seo").label("SEO").badge("3").badge_color("info").schema([
        TextInput.make("slug"),
    ]),
)
```

`.icon(...)` draws an icon on the tab button. `.badge(...)` adds a count (a string or a callable). `.badge_color(...)` tints it: `success`, `danger`, `warning`, or `info`. `.extra_attributes({...})` adds classes and data attributes on the button.

`.tabs(...)` still accepts dicts or `(label, components)` tuples when the tab needs no extra chrome:

```python title="app/orbit/schemas/tabs_defs.py"
Tabs.make("main").tabs(
    ("Account", [TextInput.make("email")]),
    ("Profile", [TextInput.make("display_name")]),
)

Tabs.make("main").tabs(
    {
        "label": "SEO",
        "icon": "heroicon-o-magnifying-glass",
        "badge": "3",
        "schema": [TextInput.make("slug")],
    },
)
```

Dict keys: `label` (or `id`), `schema` / `components`, optional `icon`, optional `badge` (string or callable).

## Icons and badges

```python title="app/orbit/schemas/tabs_badges.py"
Tabs.make("main")
    .tabs({
        "label": "SEO",
        "icon": "heroicon-o-magnifying-glass",
        "badge": "3",
        "schema": [...],
    })
```

![Tabs with badges (light)](/examples/light/schemas/tabs/with-badges.png)
![Tabs with badges (dark)](/examples/dark/schemas/tabs/with-badges.png)

![Tabs overview (light)](/examples/light/schemas/tabs.png)
![Tabs overview (dark)](/examples/dark/schemas/tabs.png)

## Active tab and persist

```python title="app/orbit/schemas/tabs_persist.py"
Tabs.make("settings")
    .tabs(...)
    .active_tab(1)       # zero-based initial tab
    .persist_tab()       # data-persist-tab for the host
```

## API reference

| Method | Role |
|--------|------|
| `.tabs` | `Tab` components, dicts, or `(label, schema)` tuples |
| `Tab.icon` | Icon on the tab button |
| `Tab.badge` | Badge text or callable |
| `Tab.badge_color` | `success`, `danger`, `warning`, or `info` |
| `.active_tab` | Zero-based initially selected tab |
| `.persist_tab` | Persist the active tab in the host |
| `.schema` | Extra children outside tab defs (rare) |
