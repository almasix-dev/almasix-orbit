---
title: Documentation versions
description: Major-version docs switching — 0.x is the latest release, main is unreleased.
---

## How versions work

The header switcher lists **major lines** and **`main`**, never every minor tag.
Each selection is a **separate documentation tree**:

| Switcher label | URL | Meaning |
| --- | --- | --- |
| **0.x** | [`/0.x/`](/0.x/) | Docs frozen at the latest 0.x **release** (today `v0.3.1`) — **latest** (default) |
| **main** | [`/main/`](/main/) | Unreleased tip from the `main` branch (opt-in) |
| **1.x** *(later)* | `/1.x/` | Docs for the 1.x package line, once that major ships |

The site root (`https://orbit.almasix.com/`) sends you to **0.x**. **Latest is always the newest major.** `main` is never the default. Minor releases land in [Release notes](/prologue/release-notes/), not as extra switcher rows.

`astro dev` on a checkout shows the **main** tree unprefixed (`http://localhost:4321/`) so you can edit pages without building both trees.

## Not on latest

If you open a line that is not the latest major — including **`main`** — a banner appears with a link back to the latest documentation.

| Package | Docs switcher |
| --- | --- |
| `almasix-orbit==0.*` | `0.x` (latest) |
| Working from unreleased `main` | `main` |
| `almasix-orbit==1.*` *(later)* | `1.x` |

Match the switcher to the package you have installed. APIs on `main` can move before the next tagged release; stay on `0.x` when you are following a published version.

## What “0.x” contains

The `/0.x/` tree is built from the newest stable `v0.*` git tag — the same docs that shipped with that release. Pages added on `main` after `v0.3.1` (plugin marketplace, later APIs) are **not** on `0.x` until the next 0.x release.

When a new 0.x tag is published, the next docs deploy rebuilds `/0.x/` from that tag automatically.

## What to read first

New to Orbit? Start at [Installation](/getting-started/installation/) and
[Quick start](/getting-started/quick-start/), then the [Features](/features/)
checklist. Package import map: [Packages](/packages/).
