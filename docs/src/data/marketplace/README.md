# Marketplace registry (synced)

Listing YAML and images no longer live in this repository.

- **Registry:** [almasix-dev/orbit-plugins](https://github.com/almasix-dev/orbit-plugins)
- **Public catalog:** [orbit.almasix.com/plugins](https://orbit.almasix.com/plugins/)
- **Submit a listing:** [Get listed](https://orbit.almasix.com/plugins/get-listed/)

Docs builds run `npm run marketplace:sync`, which clones the registry into
`docs/.marketplace/` and copies images into `docs/public/plugins/` (both
gitignored). Locally:

```bash
cd docs
npm run marketplace:sync
npm run validate:marketplace
npm run dev
```
