---
title: Overview
description: Panel navigation groups, custom items, sort, subgroups, and layout modes.
---

Orbit navigation is a sorted list of links — from resources, pages, and anything you add by hand — then folded into a layout: sidebar, top bar, or both.

```python
from almasix.orbit import Panel
from almasix.orbit.panels import NavigationGroup, NavigationItem, NavigationSubgroup

panel = (
    Panel.make("admin")
    .path("orbit")
    .navigation_layout("sidebar_topbar")  # or "sidebar" | "top" | "apps"
    .sidebar_collapsible()
    .navigation_groups([
        NavigationGroup.make("Content")
            .icon("heroicon-o-document-text")
            .sort(10),
        NavigationGroup.make("People")
            .icon("heroicon-o-users")
            .sort(20),
    ])
    .navigation_subgroups([
        NavigationSubgroup.make("Writing")
            .parent("Content")
            .icon("heroicon-o-pencil-square")
            .sort(5),
        NavigationSubgroup.make("Insights")
            .parent("Content")
            .icon("heroicon-o-chart-bar")
            .sort(10),
    ])
    .navigation_items([
        NavigationItem.make("reports")
            .label("Reports")
            .icon("heroicon-o-chart-bar")
            .url("/orbit/reports")
            .group("Content")
            .subgroup("Insights")  # or .sub_category("Insights")
            .sort(50),
    ])
)
```

## From resources & pages

Class vars become nav dicts automatically. **You do not need to register `NavigationGroup`s** for those labels to appear — groups are collected from `navigation_group` on resources and pages. Panel `NavigationGroup`s are optional metadata (icon + sort) for matching names. The same is true for `NavigationSubgroup` / `navigation_subgroup` (alias `navigation_sub_category`).

```python
class PostResource(Resource):
    navigation_label = "Posts"
    navigation_icon = "heroicon-o-pencil-square"
    navigation_group = "Content"
    navigation_subgroup = "Writing"  # optional second level
    navigation_sort = 10
```

Same knobs exist on `Page`. `panel.navigation_items()` (no args) collects everything, sorted by `sort` then label.

## Custom NavigationItem

| Method | Role |
|--------|------|
| `.url(...)` | Destination |
| `.icon(...)` | Heroicon name |
| `.group(...)` | Sidebar / root bucket |
| `.subgroup(...)` / `.sub_category(...)` | Second-level category (top-bar dropdown / sidebar accordion) |
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

## Subgroups

`NavigationSubgroup` is the second nesting level under a group. Register one when you want a shared icon or sort for that label; otherwise the subgroup name on items is enough.

```python
NavigationSubgroup.make("Writing")
    .parent("Content")  # omit / None for ungrouped roots
    .icon("heroicon-o-pencil-square")
    .sort(5)
```

| Layout | Subgroup behavior |
|--------|-------------------|
| `apps` / `sidebar_topbar` | Groups top-bar links into a dropdown |
| `sidebar` | Accordion under the parent group label |
| `top` | Items ordered under the parent group dropdown |

## Layouts

| Layout | Feel |
|--------|------|
| `sidebar` | Classic left nav; groups as section labels; subgroups as accordions |
| `top` | Everything in the top bar; groups become dropdowns |
| `sidebar_topbar` / `apps` | Sidebar shows **group roots**; top bar shows the active group’s items (Shamar-style split) |

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
