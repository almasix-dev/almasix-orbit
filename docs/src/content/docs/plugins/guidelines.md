---
title: Listing guidelines
description: What Orbit maintainers check before a plugin goes live — scope, documentation, images, packaging, and naming.
---

These are the rules a reviewer reads your submission against. Meeting them up front usually turns a review into a single approval instead of a conversation.

## Scope: is it an Orbit plugin?

A listing belongs here if the plugin only makes sense inside Orbit — it registers a panel plugin, adds a schema component, a table column, an action, an infolist entry, a widget, a theme, or a complete panel feature.

A general Python or ORM library that happens to be useful in an admin panel is not an Orbit plugin. Publish it to PyPI and link to it from your plugin’s docs instead.

## Documentation

Your listing `description` and your README are the whole pitch. A reviewer should be able to answer three questions in under a minute:

1. **What problem does it solve?** Lead with the outcome, not the implementation.
2. **How do I install it?** Show the `pip install` line and the one-liner that wires it up:

   ```python
   panel.plugin(AcmeAuditLogPlugin())
   ```

3. **What does it look like?** At least one screenshot, or a short list of concrete features when the plugin has no UI.

Write for someone who knows Orbit and nothing else. Explain your own concepts; do not assume familiarity with another admin framework.

## Images

| Asset | Ratio | Minimum size | Notes |
|-------|-------|--------------|-------|
| Thumbnail | 16:9 | 1280×720 (2560×1440 preferred) | Crop to the feature, not the whole panel |
| Screenshots | any | readable at full width | Every one needs meaningful `alt` text |
| Author avatar | 1:1 | 400×400 | JPEG or PNG |

Use site-absolute paths (`/plugins/your-slug/thumbnail.jpg`) for files you commit under `docs/public/plugins/`, or absolute `https://` URLs for images you host. Relative paths do not resolve on the marketplace and will fail validation.

If your plugin has a UI, make sure it is legible in both light and dark themes before you set `features.dark_mode: true`.

## Packaging

- Ship a `Plugin` subclass with a unique id, and keep `register` free of side effects — see [Plugin development](/panels/plugins/).
- Prefer **passive** registration: the host app calls `panel.plugin(YourPlugin())`. Do not silently create or rename panels behind the app’s back.
- Never include an `almasix/__init__.py` in your wheel. It overwrites the framework namespace and breaks every other Orbit package in the environment.
- Scope render hooks to a panel id so a second panel does not inherit your injections.
- Declare the Orbit versions you actually test against, both in your package metadata and in `orbit_versions`.
- Pin nothing you do not have to. A plugin that hard-pins `almasix-orbit==0.3.1` blocks every consumer from upgrading.

## Naming and voice

- Distribution names read best as `<vendor>-orbit-<feature>`, for example `acme-orbit-audit-log`. Do not publish under the `almasix-orbit-*` prefix; that namespace is reserved for official packages.
- Capitalize **Orbit** and **Almasix** correctly in your listing and README.
- Do not call a plugin “official”, “certified”, or “endorsed” unless Almasix maintains it. `features.official` is set by maintainers only.
- Keep the `summary` to one honest sentence. Marketing superlatives get edited out.

## Quality bar

A reviewer may ask for changes when a plugin:

- does not install on any supported Orbit version;
- duplicates a feature Orbit already ships, without saying what it does differently;
- has no license file;
- looks visually foreign inside a panel — a plugin should use Orbit’s existing components and tokens rather than importing its own design system;
- has an unclear or empty description.

## After your plugin is live

- Keep `orbit_versions` current as new Orbit releases land.
- Respond to issues. Maintainers may unlist a plugin that is broken on every supported version and has an unreachable author.
- Security problems: fix them, then tell us. If an author will not fix a reported vulnerability, we unlist the plugin.

## Related

- [Get listed](/plugins/get-listed/) — the submission steps
- [Paid vs free](/plugins/paid-vs-free/) — extra rules for commercial plugins
- [Plugin development](/panels/plugins/) — build the package
