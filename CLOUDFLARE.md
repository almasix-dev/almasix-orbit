# Cloudflare — orbit.almasix.com

The Starlight site lives in [`docs/`](./docs/) and is intended to be served as
**Worker static assets** (same pattern as [docs.almasix.com](https://docs.almasix.com)
and [almasix.com](https://almasix.com)).

## Wrangler

[`docs/wrangler.jsonc`](./docs/wrangler.jsonc) serves `./dist` as Worker assets (`ASSETS`) and runs [`docs/scripts/github-star.mjs`](./docs/scripts/github-star.mjs) first for `/api/github/*`. That Worker stars a marketplace plugin’s GitHub repository **as the visitor** (OAuth + `PUT /user/starred/{owner}/{repo}`). Do **not** use the build-time `GITHUB_TOKEN` for starring — that would star as the site, not the reader.

Without OAuth secrets the API returns `501` and the listing button opens GitHub instead. Local `astro preview` has no Worker, so it uses the same fallback.

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

### Header GitHub chip

`@almasix/starlight-theme` fetches stars/forks/release at **build time**. Anonymous
GitHub API calls from Workers Builds are often rate-limited, which used to collapse
the chip to a plain icon. Theme **0.1.1+** always keeps the pill chrome; to populate
counts, add a build env var in the Workers Builds project:

| Variable | Value |
|----------|--------|
| `GITHUB_TOKEN` | A fine-scoped PAT (or GitHub App token) with `public_repo` / metadata read |

No secrets are required in GitHub Actions for docs (build-only).

### Marketplace Star on GitHub (runtime)

Listing **Star on GitHub** calls `POST /api/github/star`. Configure a GitHub App (preferred: user permission **Starring** only, empty `GITHUB_OAUTH_SCOPE`) or a classic OAuth App (`GITHUB_OAUTH_SCOPE=public_repo`). Callback URL:

`https://orbit.almasix.com/api/github/oauth/callback`

Workers Builds / dashboard secrets (not git):

| Variable | Value |
|----------|--------|
| `GITHUB_OAUTH_CLIENT_ID` | GitHub App or OAuth App client id |
| `GITHUB_OAUTH_CLIENT_SECRET` | Client secret |
| `GITHUB_OAUTH_SCOPE` | Empty for a GitHub App with Starring; `public_repo` for a classic OAuth App |

Copy [`docs/.dev.vars.example`](./docs/.dev.vars.example) to `docs/.dev.vars` for `npx wrangler dev`. Never commit `.dev.vars`.

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
curl -sS -o /dev/null -w '%{http_code}\n' -X POST 'https://orbit.almasix.com/api/github/star?repo=almasix-dev/almasix-orbit'
```

The star route should return `401` (OAuth configured, no cookie) or `501` (secrets not set yet) — never a static 404.

(Add `docs/public/og.png` / SEO meta when you want social previews.)

## Local

```bash
cd docs
npm ci
npm test
npm run build
npx wrangler dev      # Worker + assets; copy .dev.vars.example → .dev.vars to star for real
npx wrangler deploy   # needs Cloudflare auth (local only)
```

## Notes

- Docs are **not** published to PyPI. Python packages are separate (see [PUBLISHING.md](./PUBLISHING.md)).
- Hub packaging page / `docs.almasix.com` stub linking to Orbit can be added after the custom domain is live.
