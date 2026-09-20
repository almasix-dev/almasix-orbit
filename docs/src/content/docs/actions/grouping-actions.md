---
title: Grouping actions
description: Nest actions in dropdowns, button groups, and labeled sections with ActionGroup and BulkActionGroup.
---

## Introduction

`ActionGroup` wraps nested actions as a **dropdown** (default) or a horizontal **button group**. Pass it anywhere an action list is accepted — header actions, row actions, bulk menus. `BulkActionGroup` is the same API with bulk-oriented defaults (`label="Bulk actions"`, vertical ellipsis icon).

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ActionGroup, EditAction, ViewAction, DeleteAction

ActionGroup.make([
    EditAction.make(),
    ViewAction.make(),
    DeleteAction.make(),
]).label("Actions").icon("heroicon-o-ellipsis-vertical")
```

![Orbit ActionGroup dropdown (light)](/examples/light/actions/grouping/dropdown.png)

![Orbit ActionGroup dropdown (dark)](/examples/dark/actions/grouping/dropdown.png)

## Dropdown (default)

`.dropdown()` (default `True`) renders a trigger button plus an Alpine `orbitDropdown` menu. Nested actions keep their own colors, icons, and modal attributes.

```python title="app/orbit/actions/dropdown.py"
from almasix.orbit.actions import ActionGroup, EditAction, DeleteAction

ActionGroup.make([EditAction.make().url("/edit/1"), DeleteAction.make()])
    .label("More")
    .icon("heroicon-o-ellipsis-vertical")
    .color("gray")
    .dropdown()
```

### Placement and sizing

| Method | Notes |
|--------|-------|
| `.dropdown_placement` | e.g. `bottom-end`, `top-start` — `data-dropdown-placement` |
| `.dropdown_width` | Menu width token |
| `.dropdown_offset` | Pixel offset from the trigger |
| `.dropdown_max_height` | Scroll when the menu is long |

```python title="app/orbit/actions/dropdown_placement.py"
from almasix.orbit.actions import ActionGroup, EditAction

ActionGroup.make([EditAction.make()])
    .dropdown_placement("bottom-end")
    .dropdown_width("14rem")
    .dropdown_offset(8)
    .dropdown_max_height(240)
```

Use `.icon_button()` on the group for a compact ⋮ trigger in table rows.

## Button group

`.button_group()` lays children out horizontally (`or-btn-group`) instead of a menu — good for primary toolbars.

```python title="app/orbit/actions/button_group.py"
from almasix.orbit.actions import ActionGroup, EditAction, ViewAction, DeleteAction

ActionGroup.make([
    EditAction.make().url("/edit/1"),
    ViewAction.make().url("/view/1"),
    DeleteAction.make(),
]).button_group()
```

![Orbit ActionGroup button group (light)](/examples/light/actions/grouping/button-group.png)

![Orbit ActionGroup button group (dark)](/examples/dark/actions/grouping/button-group.png)

## Sections

Nested `ActionGroup`s with `.dropdown(False)` become **labeled sections** inside a parent button group — useful for “Record” vs “Danger zone” clusters.

```python title="app/orbit/actions/sections.py"
from almasix.orbit.actions import (
    ActionGroup, EditAction, ViewAction, DeleteAction, ForceDeleteAction,
)

ActionGroup.make([
    ActionGroup.make([EditAction.make(), ViewAction.make()])
        .label("Record")
        .dropdown(False),
    ActionGroup.make([DeleteAction.make(), ForceDeleteAction.make()])
        .label("Danger zone")
        .dropdown(False),
]).button_group()
```

![Orbit ActionGroup sections (light)](/examples/light/actions/grouping/sections.png)

![Orbit ActionGroup sections (dark)](/examples/dark/actions/grouping/sections.png)

## Flattening

`.flat_actions()` walks nested groups and returns leaf actions — handy when a host needs a single list for authorization or keyboard maps.

```python title="app/orbit/actions/flat.py"
from almasix.orbit.actions import ActionGroup, EditAction, DeleteAction

group = ActionGroup.make([
    ActionGroup.make([EditAction.make()]),
    DeleteAction.make(),
])
names = [a.get_name() for a in group.flat_actions()]  # ["edit", "delete"]
```

## BulkActionGroup

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import BulkActionGroup, DeleteBulkAction

table.bulk_actions([
    BulkActionGroup.make([DeleteBulkAction.make()]).label("Bulk actions"),
])
```

Same dropdown / button-group / section APIs as `ActionGroup`.

## Visibility

If every nested action is hidden or unauthorized, the group renders empty string — no orphan trigger.
