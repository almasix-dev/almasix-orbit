# Plugin marketplace review guidelines

Maintainer-facing notes for reviewing submissions to `docs/src/data/marketplace/`.
Authors should read [Get listed](../docs/src/content/docs/plugins/get-listed.md) and
[Listing guidelines](../docs/src/content/docs/plugins/guidelines.md) instead.

## Review order

1. CI is green — `npm run validate:marketplace` and `npm test` (validator unit tests)
   run before the docs build and catch schema errors, unknown categories, dangling
   author references, reserved slugs, and missing images.
2. The PR only touches `docs/src/data/marketplace/**` and `docs/public/plugins/**`.
   A listing PR that also changes framework code goes back for a split.
3. Install the package yourself if it is free: `pip install <package>` on a supported
   Orbit version, then `panel.plugin(...)` in a scratch panel.
4. Read the listing page in a preview build. Check both themes.
5. For paid plugins, complete the private source review below before approving.

## Standard replies

Copy, adjust, and post. Keep the tone friendly; most authors are first-time contributors.

### Purpose unclear

```md
Thanks for the submission! Right now it is hard to tell from the description what the
plugin does in practice. Could you expand it with the problem it solves, the one-liner
that wires it into a panel, and a screenshot or two? Ping us here once it is updated.
```

### Not an Orbit plugin

```md
Thanks for this! Looking at the code, it reads as a general Python package rather than
something specific to Orbit — nothing in it depends on panels, schemas, tables, or
actions. The marketplace is for Orbit-specific extensions, so we are going to pass on
the listing. Publishing it to PyPI and linking it from your Orbit plugin's docs is a
great option.
```

### Image does not meet the bar

```md
Your thumbnail needs to be 16:9 and at least 1280x720 (2560x1440 preferred). It also
works best cropped to the feature itself rather than a full panel screenshot — the
sidebar and topbar take up most of the frame at card size. Let us know once it is
swapped in.
```

### Missing or relative image paths

```md
Image paths must be site-absolute (`/plugins/your-slug/thumbnail.jpg`, committed under
`docs/public/plugins/`) or absolute `https://` URLs. Relative paths will not resolve on
the marketplace.
```

### Unknown or wrong category

```md
`categories` must use keys from `docs/src/data/marketplace/categories.yaml`. Pick the
closest existing ones; if nothing fits, open an issue and we will discuss adding a
category before merging this listing.
```

### Naming and casing

```md
Small one: please capitalize "Orbit" and "Almasix" consistently in the listing and
README, and rename the distribution away from the `almasix-orbit-*` prefix — that
namespace is reserved for packages we maintain. `<vendor>-orbit-<feature>` works well.
```

### Namespace stomping

```md
The wheel ships an `almasix/__init__.py`, which overwrites the framework namespace and
breaks other Orbit packages in the same environment. Please remove it and publish a new
release before we list this.
```

### Paid plugin — private review

```md
Thanks! Since this is a paid plugin, one of us needs to review the private source before
it goes live. Please add @<maintainer> to the private repository (read access is enough)
or send a copy of the wheel. We check packaging hygiene, namespace safety, network
calls, and licensing enforcement — nothing is redistributed.
```

### Paid plugin — checkout problems

```md
The `checkout_url` needs to land on a page where a buyer can actually complete the
purchase and see the listed price. Right now it points at a marketing page, so people
would have to hunt for the product. Could you link the product page directly?
```

### Free listing that is really a trial

```md
This listing is marked free, but the package stops working without a paid license. List
it as paid with the real price, or ship a genuinely usable free edition and a separate
paid listing for the pro version.
```

### Design does not fit a panel

```md
The plugin looks quite different from the rest of a panel — it brings its own design
system rather than using Orbit's components and CSS tokens. That contrast tends to put
people off installing it. Reusing Orbit's components would help a lot here.
```

### Allow maintainer edits

```md
Could you re-open this PR with "Allow edits by maintainers" enabled? It lets us fix
small things like a category key or a typo directly instead of sending the PR back.
```

## Unlisting

Unlist (delete the YAML, keep the git history) when:

- an unpatched security issue is reported and the author is unresponsive or unwilling;
- the plugin no longer installs on any supported Orbit version and the author is unreachable;
- a paid listing's price or checkout no longer matches the registry entry after a reminder;
- the package is removed from PyPI or the store.

Always open the unlisting PR with a short reason in the description, and try to contact
the author first through their listed channels.

## Setting `features.official` / `features.featured`

- `official: true` only for plugins Almasix maintains, and only when `author` is `almasix`.
  The validator rejects official flags on other authors.
- `featured: true` is a maintainer curation call. Keep the featured row small (four or
  fewer), refresh it occasionally, and do not sell placement.
- `status: archived` hides a retired listing without deleting git history. Prefer this
  over deleting YAML when people may still hold a copy of the package.
