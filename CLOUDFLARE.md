# Cloudflare — orbit.almasix.com

The Starlight site lives in [`docs/`](./docs/) and is intended to be served as
**Worker static assets** (same pattern as [docs.almasix.com](https://docs.almasix.com)
and [almasix.com](https://almasix.com)).

## Wrangler

[`docs/wrangler.jsonc`](./docs/wrangler.jsonc) serves `./dist`. There is no Worker `main` script.

## CI vs deploy

GitHub Actions ([`.github/workflows/docs.yml`](./.github/workflows/docs.yml) and the
`docs` job in [`ci.yml`](./.github/workflows/ci.yml)) **build only**.

**Deploy** is Cloudflare **Workers Builds** (no API tokens in GitHub):

| Setting | Value |
|---------|--------|
| Repository | `almasix-dev/almasix-orbit` |
| Root directory | `docs` |
| Build command | `npm ci && npm run build` |
| Deploy command | `npx wrangler deploy` |
| Project name | `almasix-orbit-docs` |
| Node | `22` (or `24`) |

## Cutover checklist

1. Cloudflare Dashboard → **Workers & Pages** → **Create** → connect **`almasix-dev/almasix-orbit`**.
2. Set **root directory** to **`docs`** and the build/deploy commands above.
3. First production deploy must succeed.
4. **Custom domains** → add **`orbit.almasix.com`**.
5. Zone **SSL/TLS** → Full (strict) + Always Use HTTPS (if not already).
6. Wait until the domain is **Active** and the cert is issued.
7. Verify:

```bash
curl -I https://orbit.almasix.com/
curl -sS https://orbit.almasix.com/robots.txt | head
curl -sS -o /dev/null -w '%{http_code}\n' https://orbit.almasix.com/og.png
```

(Add `docs/public/og.png` / SEO meta when you want social previews.)

## Local

```bash
cd docs
npm ci
npm run build
npx wrangler deploy   # needs Cloudflare auth (local only)
```

## Notes

- Docs are **not** published to PyPI. Python packages are separate (see [PUBLISHING.md](./PUBLISHING.md)).
- Hub packaging page / `docs.almasix.com` stub linking to Orbit can be added after the custom domain is live.
