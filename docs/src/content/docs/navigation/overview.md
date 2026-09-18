---
title: Overview
description: Panel navigation groups, custom items, sort, subgroups, and layout modes.
---

Orbit navigation is a sorted list of links — from resources, pages, and anything you add by hand — then folded into a layout: sidebar, top bar, or both.

```python
from almasix.orbit import Panel
from almasix.orbit.panels import NavigationGroup, NavigationItem

panel = (
    Panel.make("admin")
    .path("orbit")
    .navigation_layout("sidebar_topbar")  # or "sidebar" | "top"
    .sidebar_collapsible()
    .navigation_groups([
        NavigationGroup.make("Content")
            .icon("heroicon-o-document-text")
            .sort(10),
        NavigationGroup.make("People")
            .icon("heroicon-o-users")
            .sort(20),
    ])
    .navigation_items([
        NavigationItem.make("reports")
            .label("Reports")
            .icon("heroicon-o-chart-bar")
            .url("/orbit/reports")
            .group("Content")
            .subgroup("Insights")
            .sort(50),
    ])
)
```

## From resources & pages

Class vars become nav dicts automatically. **You do not need to register `NavigationGroup`s** for those labels to appear — groups are collected from `navigation_group` on resources and pages. Panel `NavigationGroup`s are optional metadata (icon + sort) for matching names.

```python
class PostResource(Resource):
    navigation_label = "Posts"
    navigation_icon = "heroicon-o-pencil-square"
    navigation_group = "Content"
    navigation_subgroup = "Writing"  # optional
    navigation_sort = 10
```

Same knobs exist on `Page`. `panel.navigation_items()` (no args) collects everything, sorted by `sort` then label.

## Custom NavigationItem

| Method | Role |
|--------|------|
| `.url(...)` | Destination |
| `.icon(...)` | Heroicon name |
| `.group(...)` | Sidebar / root bucket |
| `.subgroup(...)` | Collapses into a top-bar dropdown under that label |
| `.sort(int)` | Order within the group |
| `.label(...)` | Display text (defaults from the name) |

```python
NavigationItem.make("docs")
    .label("External docs")
    .url("https://example.test/docs")
    .group("Content")
    .sort(100)
```

Pass a list to `.navigation_items([...])` to **append** custom items to the collected set. Call with no arguments to read the merged collection.

## Groups

`NavigationGroup` is **optional**. Without it, roots still form from resource/page `navigation_group` strings (icon falls back to the first item). Register a group only when you want a shared icon or sort order for that label:

```python
NavigationGroup.make("Content")
    .icon("heroicon-o-document-text")
    .sort(10)
```

## Layouts

| Layout | Feel |
|--------|------|
| `sidebar` | Classic left nav; groups as section labels |
| `top` | Everything in the top bar; subgroups become dropdowns |
| `sidebar_topbar` | Sidebar shows **group roots**; top bar shows the active group’s items (Shamar-style split) |

```python
panel.navigation_layout("sidebar_topbar")
panel.sidebar_collapsible()  # toggle collapses labels in the shell
```

```html
<div class="or-app" data-nav-layout="sidebar_topbar">
  <aside class="or-sidebar">
    <a class="or-nav-link is-active" href="/orbit/posts">Content</a>
    <a class="or-nav-link" href="/orbit/users">People</a>
  </aside>
  <div class="or-main">
    <header class="or-topbar">
      <nav class="or-topnav">
        <a class="or-topnav-link is-active" href="/orbit/posts">Posts</a>
        <div class="or-topnav-dropdown">
          <button type="button">Insights</button>
          <div class="or-topnav-menu">
            <a class="or-topnav-child" href="/orbit/reports">Reports</a>
          </div>
        </div>
      </nav>
    </header>
  </div>
</div>
```

Active matching prefers the longest URL prefix against the current path. Ungrouped items land under a catch-all “Menu” root when using the split layout.
