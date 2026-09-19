---
title: Empty states
description: Centered heading, description, icon, and actions when a list, repeater, or schema slot has nothing to show.
---

## Introduction

`EmptyState` renders a centered placeholder when lists, repeaters, or standalone schema slots have no items. Reuse the same component in tables (via table empty-state helpers) or drop it directly into a schema when a region has nothing to show yet.

```python title="app/orbit/schemas/empty_basic.py"
from almasix.orbit.schemas import EmptyState

EmptyState.make()
    .heading("No drafts")
    .description("Create one when you are ready.")
```

![Basic empty state (light)](/examples/light/schemas/empty-state/basic.png)
![Basic empty state (dark)](/examples/dark/schemas/empty-state/basic.png)

## Icon

Add a heroicon above the heading to reinforce the empty context:

```python title="app/orbit/schemas/empty_icon.py"
EmptyState.make()
    .heading("No posts yet")
    .description("Create your first post to get going.")
    .icon("heroicon-o-document-text")
```

## Actions

Attach primary / secondary actions under the body — typically a create button:

```python title="app/orbit/schemas/empty_actions.py"
from almasix.orbit.actions import Action
from almasix.orbit.schemas import EmptyState

EmptyState.make()
    .heading("No posts yet")
    .description("Create your first post to get going.")
    .icon("heroicon-o-document-text")
    .actions([
        Action.make("create").label("New post").icon("heroicon-o-plus"),
    ])
```

![Empty state (light)](/examples/light/schemas/empty-state.png)
![Empty state (dark)](/examples/dark/schemas/empty-state.png)

## Nested schema body

`.schema([...])` children render between the description and the actions row — useful for primes or secondary hints:

```python title="app/orbit/schemas/empty_nested.py"
from almasix.orbit.schemas import EmptyState, Text

EmptyState.make()
    .heading("Inbox zero")
    .schema([
        Text.make().content("You're all caught up.").color("gray"),
    ])
```

If you omit `.heading(...)`, the empty state falls back to `.label(...)` or the string “Nothing here”.

## API reference

| Method | Role |
|--------|------|
| `.heading` | Primary title |
| `.description` | Supporting copy |
| `.icon` | Heroicon above the heading |
| `.actions` | Action components under the body |
| `.schema` | Optional nested body components |

See also table-level empty state helpers on [Tables overview](/tables/overview/).
