---
title: Callout
description: Callout surfaces info, success, warning, or danger messages inside a form — tips before save, destructive confirmations, or success banners.
---

## Introduction

Callout surfaces info, success, warning, or danger messages inside a form — tips before save, destructive confirmations, or success banners.

Each variation below includes a short explanation, the fluent API to paste into your schema, and a screenshot of the rendered control.

## Info callout

Neutral guidance.

```python
Callout.make()
    .info()
    .label('Tip')
    .description('Fill these fields before saving.')
```

![Orbit Info callout (light)](/examples/light/schemas/callout/info.png)

![Orbit Info callout (dark)](/examples/dark/schemas/callout/info.png)

## Danger callout

Destructive action warning.

```python
Callout.make()
    .danger()
    .label('Danger')
    .description('This action cannot be undone.')
```

![Orbit Danger callout (light)](/examples/light/schemas/callout/danger.png)

![Orbit Danger callout (dark)](/examples/dark/schemas/callout/danger.png)

## Success callout

Confirmation feedback.

```python
Callout.make()
    .success()
    .label('Saved')
    .description('Your changes were published.')
```

![Orbit Success callout (light)](/examples/light/schemas/callout/success.png)

![Orbit Success callout (dark)](/examples/dark/schemas/callout/success.png)

## Warning callout

Caution that is not yet destructive.

```python
Callout.make()
    .warning()
    .label("Unpublished")
    .description("This draft is not visible on the site.")
```

![Orbit Warning callout (light)](/examples/light/schemas/callout/warning.png)

![Orbit Warning callout (dark)](/examples/dark/schemas/callout/warning.png)

## Footer actions

`.footer_actions([...])` renders buttons under the body. `.footer_actions_alignment("end")` (or `"start"` / `"center"`) aligns them.

```python
from almasix.orbit.actions import Action
from almasix.orbit.schemas import Callout

Callout.make()
    .warning()
    .label("Unsaved changes")
    .description("Leave this page and the draft is lost.")
    .footer_actions([Action.make("discard").label("Discard").color("danger")])
    .footer_actions_alignment("end")
```

![Orbit Callout footer actions (light)](/examples/light/schemas/callout/footer.png)

![Orbit Callout footer actions (dark)](/examples/dark/schemas/callout/footer.png)

`.icon(...)` / `.icon_color(...)` override the status default. `.color(...)` sets the accent independently of `.status(...)`. Nested `.schema([...])` lands in the body under the description.

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
