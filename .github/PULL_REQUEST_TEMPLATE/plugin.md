---
name: Plugin marketplace submission
about: Add or update a listing in the Orbit plugin marketplace
labels: marketplace
---

## Listing

- **Plugin name:**
- **Slug / registry file:** `docs/src/data/marketplace/plugins/<slug>.yaml`
- **Author profile:** `docs/src/data/marketplace/authors/<slug>.yaml`
- **Repository:**
- **Package (PyPI) or store URL:**
- **Price:** free / paid (amount + currency)

## What it does

<!-- Two or three sentences: the problem it solves and how someone uses it. -->

## Checklist

- [ ] `cd docs && npm run validate:marketplace` passes locally
- [ ] Listing renders correctly in `npm run dev` at `/plugins/<slug>/`, in light and dark
- [ ] Thumbnail is 16:9, at least 1280x720, and cropped to the feature
- [ ] Every screenshot has meaningful `alt` text
- [ ] `orbit_versions` lists versions I have actually tested
- [ ] Categories come from `docs/src/data/marketplace/categories.yaml`
- [ ] The wheel does **not** contain `almasix/__init__.py`
- [ ] Package name does not use the reserved `almasix-orbit-*` prefix
- [ ] The plugin has a license file
- [ ] This PR only touches `docs/src/data/marketplace/**` and `docs/public/plugins/**`
- [ ] "Allow edits by maintainers" is enabled

## Paid plugins only

- [ ] `checkout_url` lands on a page where a buyer can complete the purchase
- [ ] The listed price matches the store
- [ ] The license terms (projects, seats, updates, support window) are published
- [ ] I can give a maintainer read access to the private source, or send the wheel, for review

<!--
Reviewers: .github/PLUGIN_REVIEW_GUIDELINES.md
Authors: https://orbit.almasix.com/plugins/get-listed/
-->
