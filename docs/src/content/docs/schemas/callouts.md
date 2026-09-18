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

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
