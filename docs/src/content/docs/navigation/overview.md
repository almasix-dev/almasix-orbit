---
title: Overview
description: Panel navigation — layouts, groups, subgroups, badges, parent items, custom items, builder, and sidebar chrome.
---

## Introduction

**Navigation** is the sorted set of links Orbit builds from resources, pages, clusters, and anything you register by hand. Layouts fold that list into a sidebar, a top bar, or both (Shamar-style `apps`).

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit import Panel
from almasix.orbit.panels import NavigationGroup, NavigationItem, NavigationSubgroup

Panel.make("admin")
    .path("admin")
    .navigation_layout("apps")  # or "sidebar" | "top" | "sidebar_topbar"
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
    ])
    .navigation_items([
        NavigationItem.make("reports")
            .label("Reports")
            .icon("heroicon-o-chart-bar")
            .url("/admin/reports")
            .group("Content")
            .subgroup("Insights")
            .sort(50),
    ])
```

![Orbit Navigation overview (light)](/examples/light/navigation/overview.png)

![Orbit Navigation overview (dark)](/examples/dark/navigation/overview.png)

Related: [Custom pages](/navigation/custom-pages/), [User menu](/navigation/user-menu/), [Clusters](/navigation/clusters/).

## From resources & pages

Class vars become nav dicts automatically. **You do not need to register `NavigationGroup`s** for those labels to appear — groups are collected from `navigation_group` on resources and pages. Panel `NavigationGroup`s are optional metadata (icon + sort) for matching names. The same is true for `NavigationSubgroup` / `navigation_subgroup` (alias `navigation_sub_category`).

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit import Resource

class PostResource(Resource):
    navigation_label = "Posts"
    navigation_icon = "heroicon-o-pencil-square"
    active_navigation_icon = "heroicon-s-pencil-square"
    navigation_group = "Content"
    navigation_subgroup = "Writing"
    navigation_sort = 10
    navigation_badge = "3"
    navigation_badge_color = "danger"
    navigation_badge_tooltip = "Drafts waiting"
```

Same knobs exist on `Page`. `panel.navigation_items()` (no args) collects everything, sorted by `sort` then label.

| Class var | Role |
|-----------|------|
| `navigation_label` | Sidebar / topbar text |
| `navigation_icon` / `active_navigation_icon` | Heroicon; active swap when the item is current |
| `navigation_group` | Root bucket / sidebar section |
| `navigation_subgroup` / `navigation_sub_category` | Second-level category |
| `navigation_sort` | Ascending order within the group |
| `navigation_badge` / `_color` / `_tooltip` | Badge chrome (string or callable via getters) |
| `navigation_parent_item` | Nest under another item’s label |
| `should_register_navigation` | Omit from nav when `False` |

## Layouts

| Layout | Feel |
|--------|------|
| `sidebar` | Classic left nav; groups as section labels; subgroups as accordions |
| `top` | Everything in the top bar; groups become dropdowns |
| `sidebar_topbar` / `apps` | Sidebar shows **group roots**; top bar shows the active group’s items |

```python title="app/providers/orbit_panel_provider.py"
Panel.make("admin").path("admin").apps_navigation()
Panel.make("admin").path("admin").sidebar_navigation()
Panel.make("admin").path("admin").top_navigation()
```

![Orbit Navigation apps layout (light)](/examples/light/navigation/overview/layouts-apps.png)

![Orbit Navigation apps layout (dark)](/examples/dark/navigation/overview/layouts-apps.png)

![Orbit Navigation sidebar layout (light)](/examples/light/navigation/overview/layouts-sidebar.png)

![Orbit Navigation sidebar layout (dark)](/examples/dark/navigation/overview/layouts-sidebar.png)

![Orbit Navigation top layout (light)](/examples/light/navigation/overview/layouts-top.png)

![Orbit Navigation top layout (dark)](/examples/dark/navigation/overview/layouts-top.png)

Active matching prefers the longest URL prefix against the current path. Ungrouped items land under a catch-all “Menu” root when using the split layout.

## Groups

`NavigationGroup` is **optional**. Without it, roots still form from resource/page `navigation_group` strings (icon falls back to the first item). Register a group when you want a shared icon, sort order, or collapse defaults:

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit.panels import NavigationGroup

NavigationGroup.make("Content")
    .icon("heroicon-o-document-text")
    .sort(10)
    .collapsed()           # start closed
    .collapsible(True)     # allow toggle (default)

Panel.make("admin")
    .path("admin")
    .collapsible_navigation_groups()  # panel-wide default
    .navigation_groups([
        NavigationGroup.make("Content").icon("heroicon-o-document-text").sort(10),
        "People",  # label-only — sets group order
    ])
```

![Orbit Navigation groups (light)](/examples/light/navigation/overview/groups.png)

![Orbit Navigation groups (dark)](/examples/dark/navigation/overview/groups.png)

| Method | Notes |
|--------|-------|
| `.icon` | Shared group icon (sidebar roots / top dropdowns) |
| `.sort` | Order among named groups |
| `.collapsed` | Start collapsed (`bool` or callable) |
| `.collapsible` | Whether the group can toggle |
| `.items` | Nest fluent `NavigationItem`s; also registers them on the panel |
| `.extra_sidebar_attributes` / `.extra_topbar_attributes` | Extra HTML attrs on the wrapper |

## Subgroups

`NavigationSubgroup` is the second nesting level under a group. Register one for a shared icon or sort; otherwise the subgroup name on items is enough.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit.panels import NavigationSubgroup

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

![Orbit Navigation subgroups (light)](/examples/light/navigation/overview/subgroups.png)

![Orbit Navigation subgroups (dark)](/examples/dark/navigation/overview/subgroups.png)

## Badges

Set `navigation_badge` (and optional color / tooltip) on a resource or page, or chain `.badge(...)` on a `NavigationItem`. Colors mirror Orbit semantic tokens: `primary`, `danger`, `success`, `warning`, `info`, `gray`.

```python title="app/orbit/resources/inbox_resource.py"
class InboxResource(Resource):
    navigation_label = "Inbox"
    navigation_badge = "3"
    navigation_badge_color = "danger"
    navigation_badge_tooltip = "Unread"
```

![Orbit Navigation badges (light)](/examples/light/navigation/overview/badges.png)

![Orbit Navigation badges (dark)](/examples/dark/navigation/overview/badges.png)

## Parent items

Nest an item under another by label with `navigation_parent_item` (or `.parent_item(...)` on `NavigationItem`). Parent and child should share the same `navigation_group`.

```python title="app/orbit/pages/preferences_page.py"
class SettingsPage(Page):
    navigation_label = "Settings"
    navigation_group = "System"
    navigation_icon = "heroicon-o-cog-6-tooth"

class PreferencesPage(Page):
    navigation_label = "Preferences"
    navigation_group = "System"
    navigation_parent_item = "Settings"
```

![Orbit Navigation parent items (light)](/examples/light/navigation/overview/parent-items.png)

![Orbit Navigation parent items (dark)](/examples/dark/navigation/overview/parent-items.png)

For a third level of hierarchy, prefer [Clusters](/navigation/clusters/) instead of stacking parent items.

## Custom NavigationItem

Append hand-built links with `.navigation_items([...])` or `.navigation_item(...)`. Call `.navigation_items()` with no arguments to read the merged collection.

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit.panels import NavigationItem

NavigationItem.make("docs")
    .label("External docs")
    .url("https://example.test/docs")
    .icon("heroicon-o-book-open")
    .group("Content")
    .sort(100)
    .open_url_in_new_tab()
    .is_active_when(lambda active_path, **_: active_path == "/admin/docs")
```

![Orbit Navigation custom items (light)](/examples/light/navigation/overview/custom-items.png)

![Orbit Navigation custom items (dark)](/examples/dark/navigation/overview/custom-items.png)

| Method | Notes |
|--------|-------|
| `.url` | Destination |
| `.icon` / `.active_icon` | Heroicon names |
| `.group` / `.subgroup` / `.sub_category` | Nesting |
| `.sort` | Order within the group |
| `.label` | Display text (defaults from the name) |
| `.badge` / `.badge_color` / `.badge_tooltip` | Badge chrome |
| `.open_url_in_new_tab` | `target="_blank"` when true |
| `.is_active_when` | Callable override for active state |
| `.parent_item` | Nest under another item’s label |
| `.visible` | Hide when false (from `Component`) |

## Disabling registration

Set `should_register_navigation = False` (or override `get_should_register_navigation`) on a resource or page to keep the route but omit the nav link.

```python title="app/orbit/resources/secret_resource.py"
class SecretResource(Resource):
    should_register_navigation = False
```

## Navigation builder

`.navigation(...)` disables the nav (`False`), restores auto collection (`True`), or replaces items entirely with a `NavigationBuilder` / callable:

```python title="app/providers/orbit_panel_provider.py"
from almasix.orbit.panels import NavigationBuilder, NavigationItem

Panel.make("admin")
    .path("admin")
    .navigation(
        NavigationBuilder.make()
            .items([
                NavigationItem.make("home")
                    .label("Home")
                    .url("/admin")
                    .icon("heroicon-o-home"),
            ])
    )

# Or a callable:
Panel.make("admin").navigation(
    lambda builder: builder.items([
        NavigationItem.make("home").label("Home").url("/admin"),
    ])
)

Panel.make("admin").navigation(False)  # hide chrome nav entirely
```

## Sidebar collapse & width

```python title="app/providers/orbit_panel_provider.py"
Panel.make("admin")
    .path("admin")
    .sidebar_collapsible()                    # icon rail on desktop
    .sidebar_fully_collapsible_on_desktop()   # hide sidebar when collapsed
    .sidebar_width("18rem")
    .collapsed_sidebar_width("4.5rem")
```

![Orbit Navigation sidebar collapse (light)](/examples/light/navigation/overview/sidebar-collapse.png)

![Orbit Navigation sidebar collapse (dark)](/examples/dark/navigation/overview/sidebar-collapse.png)

`.sidebar_collapsible_on_desktop()` is an alias for `.sidebar_collapsible()`.

## Breadcrumbs

Breadcrumbs are on by default. Toggle with `.breadcrumbs_enabled(False)`. Cluster-aware trails include the cluster breadcrumb — see [Clusters](/navigation/clusters/).
