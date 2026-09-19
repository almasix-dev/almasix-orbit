---
title: Callouts
description: Surface info, success, warning, or danger messages inside a schema — tips, confirmations, and footer actions.
---

## Introduction

`Callout` surfaces status messages inside a form or page schema — tips before save, destructive confirmations, or success banners. Status helpers set both the semantic role and default icon / color.

```python title="app/orbit/schemas/callout_info.py"
from almasix.orbit.schemas import Callout

Callout.make()
    .info()
    .label("Tip")
    .description("Fill these fields before saving.")
```

![Info callout (light)](/examples/light/schemas/callout/info.png)
![Info callout (dark)](/examples/dark/schemas/callout/info.png)

## Status helpers

```python title="app/orbit/schemas/callout_status.py"
Callout.make().info().label("Tip").description("…")
Callout.make().success().label("Saved").description("…")
Callout.make().warning().label("Check").description("…")
Callout.make().danger().label("Danger").description("…")
# or: .status("info" | "success" | "warning" | "danger")
```

![Danger callout (light)](/examples/light/schemas/callout/danger.png)
![Danger callout (dark)](/examples/dark/schemas/callout/danger.png)

![Success callout (light)](/examples/light/schemas/callout/success.png)
![Success callout (dark)](/examples/dark/schemas/callout/success.png)

![Callout (light)](/examples/light/schemas/callout.png)
![Callout (dark)](/examples/dark/schemas/callout.png)

## Icons and colors

Override the default status icon / color when needed:

```python title="app/orbit/schemas/callout_icon.py"
Callout.make()
    .warning()
    .label("Storage")
    .description("Disk is 90% full.")
    .icon("heroicon-o-server-stack")
    .icon_color("danger")
    .color("warning")
```

## Footer actions

Attach action buttons under the callout body:

```python title="app/orbit/schemas/callout_footer.py"
from almasix.orbit.actions import Action
from almasix.orbit.schemas import Callout

Callout.make()
    .danger()
    .label("Delete project")
    .description("This action cannot be undone.")
    .footer_actions([
        Action.make("confirm").label("Delete").color("danger"),
    ])
    .footer_actions_alignment("end")
```

You can also nest schema children via `.schema([...])` inside the callout body.

## API reference

| Method | Role |
|--------|------|
| `.info` / `.success` / `.warning` / `.danger` | Status helpers |
| `.status` | Explicit status string |
| `.label` | Title text |
| `.description` | Supporting copy |
| `.icon` / `.icon_color` / `.color` | Visual overrides |
| `.footer_actions` | Action components in the footer |
| `.footer_actions_alignment` | e.g. `start` / `end` |
| `.schema` | Nested body components |
