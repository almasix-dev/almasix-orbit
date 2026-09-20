---
title: Documentation versions
description: Major-version docs switching — latest major by default, main for unreleased.
---

## How versions work

The docs header switcher lists **major lines** and **`main`**, never every
minor tag:

| Switcher label | Meaning |
| --- | --- |
| **0.x** | Docs for the 0.x package line — **latest** (default) |
| **main** | Unreleased tip from the `main` branch (opt-in) |
| **1.x** *(later)* | Docs for the 1.x package line, once that major ships |

**Latest is always the newest major** (`0.x` today). `main` is never the
default. Minor releases land in [Release notes](/prologue/release-notes/),
not as separate documentation trees.

## Not on latest

If you open a line that is not the latest major — including **`main`** — a
banner appears with a link back to the latest documentation.

| Package | Docs switcher |
| --- | --- |
| `almasix-orbit==0.*` | `0.x` (latest) |
| Working from unreleased `main` | `main` |
| `almasix-orbit==1.*` *(later)* | `1.x` |

Match the switcher to the package you have installed. APIs on `main` can
move before the next tagged release; copy from `0.x` when you are following
a published version.

## Parallel trees

Today the site is a single corpus. Selecting a non-latest line sets
`?docsVersion=` so the switcher and banner stay in sync in the browser. When
**1.x** ships, archived major trees (`/0.x/…`, `/1.x/…`) will hold frozen page
sets — same switcher behaviour, with real path prefixes.

## What to read first

New to Orbit? Start at [Installation](/getting-started/installation/) and
[Quick start](/getting-started/quick-start/), then the [Features](/features/)
checklist. Package import map: [Packages](/packages/).
