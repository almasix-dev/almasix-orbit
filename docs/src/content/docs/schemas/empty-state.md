---
title: Empty state
description: EmptyState renders a centered heading, description, icon, and actions when a list or repeater has no items.
---

## Introduction

`EmptyState` is a schema layout for “nothing here yet.” Use it inside a form or infolist when a repeater, relation, or custom slot has zero rows. Tables have their own empty chrome (`.empty_state_heading` / `.empty_state_description` on `Table`) that paints the same visual language on the index page.

Each variation below includes a short explanation, the fluent API, and a screenshot of the rendered control.

## Basic empty state

Heading plus a short description. The default heading is **Nothing here** when you omit `.heading()` and `.label()`.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.schemas import EmptyState

EmptyState.make()
    .heading("No drafts")
    .description("Create one when you are ready.")
```

![Orbit Basic empty state (light)](/examples/light/schemas/empty-state/basic.png)

![Orbit Basic empty state (dark)](/examples/dark/schemas/empty-state/basic.png)

## Icon

`.icon(...)` renders a Heroicon above the heading so the slot reads as a destination, not an error.

```python title="app/orbit/resources/post_resource.py"
EmptyState.make()
    .heading("No comments")
    .description("They will appear here after readers reply.")
    .icon("heroicon-o-chat-bubble-left-right")
```

![Orbit Empty state with icon (light)](/examples/light/schemas/empty-state/with-icon.png)

![Orbit Empty state with icon (dark)](/examples/dark/schemas/empty-state/with-icon.png)

## Actions

`.actions([...])` is a slot for [Action](/actions/overview/) buttons under the description — typically a Create that jumps to the resource create page.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import CreateAction
from almasix.orbit.schemas import EmptyState

EmptyState.make()
    .heading("No posts yet")
    .description("Write the first one.")
    .actions([CreateAction.make().url("/admin/posts/create")])
```

![Orbit Empty state with actions (light)](/examples/light/schemas/empty-state/with-actions.png)

![Orbit Empty state with actions (dark)](/examples/dark/schemas/empty-state/with-actions.png)

## Nested schema

Children passed to `.schema([...])` render between the description and the action row. Use that for a short hint field or a secondary callout.

## API cheat sheet

| Method | Role |
|--------|------|
| `.heading(text)` | Title (falls back to the component label, then “Nothing here”) |
| `.description(text)` | Paragraph under the heading |
| `.icon(name)` | Heroicon above the heading |
| `.actions([...])` | Buttons under the copy |
| `.schema([...])` | Nested components |

Tables: [Rendering a table](/components/table/). Closures on `.visible()` still apply — see [Form closures](/forms/closures/).
