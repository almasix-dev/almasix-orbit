# Orbit Demo — Orbit Records catalog

Public showcase of [Orbit](https://orbit.almasix.com/) on Almasix + Conduit +
**SQLite**. Domain: a fictional label catalog (**Artists → Albums → Tracks**)
wired to exercise dashboards, widgets, resources, relation managers, rich forms,
tables, infolists, custom pages, import/export, query builder, soft deletes,
notifications, SPA mode, and theme switching.

Kitchen-sink API galleries stay in [`../orbit-admin`](../orbit-admin).

## Feature map

| Area | What to open |
|------|----------------|
| Dashboard | Stats, Chart.js releases, ApexCharts streams, recent albums table |
| Artists | Avatar upload, tags, color, platforms, albums relation manager, infolist |
| Albums | Wizard form, ModalTableSelect artist, cover upload, money, rich notes, KeyValue, query builder, import/export, tracks relation manager |
| Tracks | Soft deletes, ternary filter, global search |
| Insights | Custom page + release checklist Wizard |
| Chrome | Theme switcher, dark mode, database notifications, SPA |

**Omitted on purpose** (see orbit-admin / docs): MFA, tenancy/billing, MorphTo,
Builder blocks, Code/Markdown editors, editable columns.

## Local setup

```bash
cd examples/demo
./scripts/bootstrap.sh
source .venv/bin/activate
smith migrate --seed
smith serve
```

Open the printed URL (panel at `/`).

**Demo login:** `demo@orbit.test` / `secret`

`bootstrap.sh` installs local Almasix / Orbit / Conduit checkouts when the
sibling repos exist; otherwise it uses PyPI.

## Deploy on Render (free)

Render Free can run this ASGI app. The SQLite file is **ephemeral** (lost on
spin-down, restart, and redeploy). That is intentional: the Docker entrypoint
always runs `smith migrate --force --seed`.

### Option A — Blueprint

1. Push this repo to GitHub.
2. Render Dashboard → **New** → **Blueprint** → select the repo.
3. Blueprint file: `examples/demo/render.yaml` (build context = repo root).
4. Set `APP_URL` to the service URL once known.
5. Deploy. Health check: `/login`.

### Option B — Web Service (Docker)

1. **New** → **Web Service** → connect the repo.
2. Root directory: leave empty / repo root (not `examples/demo`).
3. Dockerfile path: `examples/demo/Dockerfile`.
4. Runtime: **Docker**. Instance: **Free**.
5. Env vars (minimum):

| Key | Value |
| --- | --- |
| `APP_ENV` | `production` |
| `APP_DEBUG` | `false` |
| `APP_KEY` | generate (or paste a `base64:…` key) |
| `APP_URL` | `https://your-service.onrender.com` |
| `DB_CONNECTION` | `sqlite` |
| `DB_DATABASE` | `/app/database/database.sqlite` |
| `SESSION_SECURE_COOKIE` | `true` |

### GitHub Actions deploy

After the service exists, redeploys are triggered by
[`.github/workflows/deploy-demo.yml`](../../.github/workflows/deploy-demo.yml)
when **CI** succeeds on `main` (and demo-relevant paths changed), or via
**Actions → Deploy demo → Run workflow**.

1. Create the service with Option A or B above if you have not already.
2. Render → **orbit-demo** → **Settings** → **Deploy Hook** → copy the URL.
3. GitHub → repo **Settings** → **Secrets and variables** → **Actions** →
   New repository secret:
   - Name: `RENDER_DEPLOY_HOOK_URL`
   - Value: the deploy hook URL
4. Render → **Settings** → **Auto-Deploy** → **Off** (this workflow owns deploys;
   leaving Auto-Deploy on causes double builds).
5. Set `APP_URL` to your public `https://….onrender.com` URL.

### Durable SQLite (optional, paid)

1. Upgrade to **Starter**.
2. Attach a disk mounted at `/app/database`.
3. Keep `DB_DATABASE=/app/database/database.sqlite`.
4. Prefer migrate without re-seeding every boot, or keep `--seed` (seeders no-op when rows exist).

## Docker locally

From the **monorepo root**:

```bash
docker build -f examples/demo/Dockerfile -t orbit-demo .
docker run --rm -p 8000:8000 \
  -e APP_KEY=base64:orbit-demo-local-dev-key-change-me \
  -e APP_URL=http://127.0.0.1:8000 \
  -e SESSION_SECURE_COOKIE=false \
  orbit-demo
```

## Seed data

Idempotent catalog seeder: **8 artists**, **15 albums**, **~60 tracks** with
varied play counts, formats, and statuses so widgets and charts look real.
