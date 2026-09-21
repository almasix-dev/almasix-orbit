---
title: Write an article
description: Publish a marketplace article — Markdown body, images, tags, and the pull request against orbit-plugins.
---

Marketplace **articles** are full write-ups on [orbit.almasix.com/articles](/articles/). They live in the same [orbit-plugins](https://github.com/almasix-dev/orbit-plugins) registry as plugin listings, but they are editorial pages — not installable packages.

Use an article when you want to teach a workflow, announce a pattern, or walk through a plugin in more depth than a listing description allows. For a package card with `pip install`, use [Get listed](/plugins/get-listed/) instead.

![Marketplace articles browse (light)](/examples/light/articles/browse.png)

![Marketplace articles browse (dark)](/examples/dark/articles/browse.png)

## Before you start

- You have (or will add) an [author profile](/plugins/get-listed/#1-add-your-author-profile) in the registry.
- The article body is ready as Markdown (headings, code fences, and links all render).
- Optional: a 16:9 thumbnail and any figures under `public/articles/<slug>/`.

## Where articles live

```text
https://github.com/almasix-dev/orbit-plugins
  articles/
    your-slug.yaml
  public/articles/
    your-slug/
      thumbnail.png
      figure.png
```

Copy `articles/example-article.yaml`, fill it in, and set `status: published`. Images use site-absolute paths such as `/articles/your-slug/thumbnail.png` (the docs site copies them at build time).

## Field reference

| Field | Required | Notes |
|-------|----------|-------|
| `name` | yes | Display title. |
| `slug` | yes | Kebab-case; must match the filename; becomes `/articles/<slug>/`. |
| `summary` | yes | One sentence, 200 characters max. Shown on the card. |
| `body` | yes | Full Markdown for the article page. |
| `author` | yes | An author slug from `authors/`. |
| `tags` | no | Freeform tokens for browse filters (e.g. `marketplace`, `tutorial`). |
| `related_plugins` | no | Plugin slugs that must be **published** when the article is published. |
| `thumbnail` | recommended | Hero / card image. |
| `images` | no | Gallery figures; each needs `src` and descriptive `alt` text. |
| `canonical_url` | no | Optional external original; the Orbit page must still stand alone. |
| `features.official` | no | Reserved for Almasix (`author: almasix`). |
| `features.featured` | no | Set by maintainers. |
| `status` | no | `published` (default), `draft`, or `archived`. |
| `published_at` | yes | `YYYY-MM-DD`. |

Do **not** copy plugin fields such as `price`, `package`, `orbit_versions`, or plugin `categories` into an article file.

![Marketplace article detail (light)](/examples/light/articles/listing.png)

![Marketplace article detail (dark)](/examples/dark/articles/listing.png)

## Check locally

```bash title="terminal"
git clone https://github.com/almasix-dev/orbit-plugins.git
cd orbit-plugins
npm ci
npm run validate
npm test
npm run build   # preview under dist/articles/
```

## Open the pull request

Use the [new article](https://github.com/almasix-dev/orbit-plugins/compare?template=new-article.md) or [edit article](https://github.com/almasix-dev/orbit-plugins/compare?template=edit-article.md) template. Keep the diff to `articles/**`, related author YAML if needed, and `public/articles/**`.

After merge, [/articles](/articles/) rebuilds from the registry — no second PR against almasix-orbit.

## Related

- [Browse articles](/articles/)
- [Get listed](/plugins/get-listed/) — plugin listings
- [How the marketplace works](/plugins/overview/)
- [Listing guidelines](/plugins/guidelines/)
