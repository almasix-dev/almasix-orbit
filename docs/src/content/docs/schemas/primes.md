---
title: Primes
description: Primes are read-only display components — text badges, icons, images, and lists — for infolists and inline form summaries without editable state.
---

## Introduction

Primes are read-only display components — text badges, icons, images, and lists — for infolists and inline form summaries without editable state.

The screenshots below show how each variation renders in Orbit. Each section includes the fluent API used to produce it.

## Text prime

![Orbit Text prime (light)](/examples/light/schemas/primes/text.png)

![Orbit Text prime (dark)](/examples/dark/schemas/primes/text.png)

Badge-styled status text.

```python
(
    Text.make()
    .content('Published')
    .badge()
    .color('success')
)
```

## Icon prime

![Orbit Icon prime (light)](/examples/light/schemas/primes/icon.png)

![Orbit Icon prime (dark)](/examples/dark/schemas/primes/icon.png)

Heroicon with color and size.

```python
(
    Icon.make()
    .icon('heroicon-o-check')
    .color('success')
    .size('lg')
)
```

## Image prime

![Orbit Image prime (light)](/examples/light/schemas/primes/image.png)

![Orbit Image prime (dark)](/examples/dark/schemas/primes/image.png)

Avatar or thumbnail display.

```python
(
    Image.make()
    .src('https://api.dicebear.com/9.x/shapes/svg?seed=orbit')
    .image_size(48)
)
```

## List prime

![Orbit List prime (light)](/examples/light/schemas/primes/list.png)

![Orbit List prime (dark)](/examples/dark/schemas/primes/list.png)

Bulleted unordered list.

```python
(
    UnorderedList.make()
    .items(['Tables', 'Forms', 'Panels'])
    .bullet_size('sm')
)
```

Closures work on `.label()`, `.helper_text()`, `.placeholder()`, `.visible()`, `.disabled()`, and `.required()` where applicable — see [Form closures](/forms/closures/).
