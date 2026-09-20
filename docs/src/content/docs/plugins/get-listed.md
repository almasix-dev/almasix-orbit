---
title: Get listed
description: Publish an Orbit plugin and add it to the marketplace — registry fields, images, author profile, and the pull request.
---

Listing a plugin takes one pull request against the Orbit repository. You add two small YAML files — an author profile and the listing itself — plus a thumbnail. A maintainer reviews it against the [listing guidelines](/plugins/guidelines/), and once merged the plugin appears on [/plugins](/plugins/) on the next docs deploy.

## Before you start

- Your plugin works on a supported Orbit version and has a README that explains what it does.
- Free plugins are published to PyPI (`pip install your-plugin` must work). Paid plugins have a working checkout page.
- You have a 16:9 thumbnail that shows the feature, not a full screenshot of a panel.

If you have not written the plugin yet, start at [Plugin development](/panels/plugins/).

## Where the registry lives

```text
docs/src/data/marketplace/
  categories.yaml          # the allowed category list (maintainer-owned)
  authors/
    your-handle.yaml       # one file per author, filename = slug
  plugins/
    your-plugin.yaml       # one file per listing, filename = slug
```

Images live under `docs/public/plugins/` and are referenced with site-absolute paths such as `/plugins/your-plugin/thumbnail.jpg`. You may also point at an `https://` URL you control.

`plugins/example-plugin.yaml` and `authors/example-author.yaml` are filled-in templates carrying `status: draft`, so they never appear on the site. Copy one rather than starting from a blank file. The live official sample is `orbit-branding` — use it to see a published listing, not as a template to overwrite.

Filters on `/plugins` are shareable query strings (`?q=`, `price=`, `category=`, `version=`, `sort=`, `official=1`, `dark=1`). After you merge, confirm your card shows up with those filters cleared.

## 1. Add your author profile

Skip this if you already have one.

```yaml title="docs/src/data/marketplace/authors/your-handle.yaml"
name: Your Name
slug: your-handle
bio: One or two sentences about you or your company. This shows on your author page.
avatar: /plugins/authors/your-handle.jpg   # 1:1, at least 400x400
website: https://example.com
github: your-github-handle
sponsor_url: https://github.com/sponsors/your-github-handle
```

Only `name`, `slug`, and `bio` are required, and `slug` must match the filename.

![Orbit plugin author page (light)](/examples/light/plugins/author.png)

![Orbit plugin author page (dark)](/examples/dark/plugins/author.png)

Need a category that is not in `categories.yaml`? Open a [marketplace category issue](https://github.com/almasix-dev/almasix-orbit/issues/new?template=marketplace-category.yml) before you send the listing PR.

## 2. Add the listing

````yaml title="docs/src/data/marketplace/plugins/acme-audit-log.yaml"
name: Acme Audit Log
slug: acme-audit-log
summary: Records every create, edit, and delete in your panels and shows them in a resource.
description: |
  ## What it does

  Adds an `AuditLogResource` and a panel plugin that records model changes
  as your users work. Filter by user, model, or date range.

  ## Install

  ```bash
  pip install acme-orbit-audit-log
  ```

  ```python
  panel.plugin(AuditLogPlugin())
  ```
author: your-handle
categories:
  - panel-kit
  - developer-tool
orbit_versions:
  - "0.3"
price: free
package: acme-orbit-audit-log
repository: https://github.com/your-handle/acme-orbit-audit-log
docs_url: https://acme.example.com/docs/audit-log
thumbnail: /plugins/acme-audit-log/thumbnail.jpg
screenshots:
  - src: /plugins/acme-audit-log/timeline.png
    alt: Audit log timeline filtered to a single user
features:
  dark_mode: true
published_at: 2026-09-20
````

A paid listing swaps the price block and adds a checkout link:

```yaml title="docs/src/data/marketplace/plugins/acme-audit-log-pro.yaml"
price:
  amount: 79
  currency: USD
checkout_url: https://store.example.com/acme-audit-log-pro
```

### Field reference

| Field | Required | Notes |
|-------|----------|-------|
| `name` | yes | Display name. Capitalize Orbit correctly if you use it. |
| `slug` | yes | Kebab-case, must match the filename, becomes `/plugins/<slug>/`. |
| `summary` | yes | One sentence, 200 characters max. Shown on the card. |
| `description` | yes | Markdown. Headings, code fences, and links all render. |
| `author` | yes | An author slug from `authors/`. |
| `categories` | yes | One or more keys from `categories.yaml`. |
| `orbit_versions` | yes | Versions you actually support, e.g. `["0.3"]`. |
| `price` | yes | `free`, or `{ amount, currency }` with an ISO 4217 code. |
| `checkout_url` | paid only | Where a buyer completes the purchase. |
| `package` | free plugins | PyPI name; drives the `pip install` line. |
| `repository` | recommended | Public source. Required for free plugins without a PyPI name. |
| `docs_url` | no | External documentation. |
| `homepage` | no | Marketing or product page. |
| `changelog_url` | no | Release notes. |
| `license` | recommended | SPDX id such as `MIT` or `LicenseRef-Proprietary`. |
| `keywords` | no | Extra search tokens on the browse grid. |
| `requires_python` | no | e.g. `>=3.11`. |
| `thumbnail` | recommended | 16:9, at least 1280×720, JPEG or PNG. |
| `screenshots` | no | Each needs `src` and descriptive `alt` text. |
| `features.dark_mode` | no | Set `true` only if you have verified both themes. |
| `features.official` | no | Reserved for Almasix-maintained plugins (`author: almasix`). |
| `features.featured` | no | Set by maintainers, not by authors. |
| `status` | no | `published` (default), `draft` to stage, or `archived` to hide a retired plugin. |
| `published_at` | yes | `YYYY-MM-DD`. Drives the default “Newest” sort. |

## 3. Add your images

Put files under `docs/public/plugins/<your-slug>/`. Keep the thumbnail under about 400 KB — it loads on the browse grid. Crop tightly on the feature: a full panel screenshot with sidebar and topbar reads as noise at card size.

## 4. Check it locally

```bash title="terminal"
cd docs
npm ci
npm run validate:marketplace   # schema, cross-references, missing images
npm test                       # validator unit tests
npm run dev                    # then open http://localhost:4321/plugins/
```

`validate:marketplace` also runs before every docs build, so a broken entry fails CI rather than shipping a half-rendered card.

## 5. Open the pull request

```bash title="terminal"
git checkout -b plugin/acme-audit-log
git add docs/src/data/marketplace docs/public/plugins
git commit -m "Add Acme Audit Log to the plugin marketplace"
git push -u origin HEAD
gh pr create --title "Plugin: Acme Audit Log" --body "New marketplace listing"
```

Open the PR with the [plugin submission template](https://github.com/almasix-dev/almasix-orbit/compare?template=plugin.md), keep it to your listing and images, and leave “Allow edits by maintainers” enabled so a reviewer can fix small things instead of sending the PR back.

## Updating or removing a listing

- **Update:** edit your YAML file and open another PR. Bump `orbit_versions` when you add support for a new release.
- **Pause:** set `status: draft` to hide a listing without deleting its history.
- **Retire:** set `status: archived` when the plugin is no longer offered. Same hiding rules as draft, with a clearer intent.
- **Remove:** delete the YAML file and your images. Tell us in the PR description why, so we can redirect people if the plugin was popular.

Abandoned plugins that no longer install on any supported Orbit version may be unlisted by maintainers after we try to contact you.

## Related

- [Using a plugin](/plugins/using/) — what visitors do after they find you
- [Listing guidelines](/plugins/guidelines/) — what reviewers check
- [Paid vs free](/plugins/paid-vs-free/) — rules for commercial plugins
- [Plugin development](/panels/plugins/) — the code side
