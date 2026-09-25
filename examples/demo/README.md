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
| Dashboard | Stats (sparklines + links), Chart.js bar / line / doughnut, ApexCharts area, recent albums table |
| Artists | Avatar upload, tags, color, platforms, albums relation manager, infolist |
| Albums | Wizard form, ModalTableSelect artist, cover upload, money, rich notes, KeyValue, query builder, import/export, tracks relation manager |
| Tracks | Soft deletes, ternary filter, global search |
| Insights | Analytics dashboard — pie, radar, Apex donut / bar, top tracks table, release checklist Wizard |
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

`bootstrap.sh` installs the demo app editable and pulls **Almasix / Orbit /
Conduit from PyPI** only (no monorepo path installs or local editables).
Requires `almasix-orbit>=0.4.3` for `.database_notifications_using_almasix()`.
Bump versions in `pyproject.toml` when you need newer published APIs.

## Notifications

Database notifications use Almasix's polymorphic **`notifications`** table
(generate with `smith notifications:table`, then migrate). The panel wires
`.database_notifications_using_almasix()` so the bell shares that inbox.

- **User:** `User` mixes in `Notifiable`.
- **Seed:** `NotificationSeeder` writes a few unread rows for `demo@orbit.test`.
- **Live:** creating, updating, or deleting Artists / Albums / Tracks notifies
  the signed-in user (header bell). Try saving an artist while logged in.

## Soft catalog reset (keeps sessions)

Sessions use the **cookie** driver, so they are not stored in SQLite. A full
`migrate:fresh` would wipe users and force re-login; instead the demo uses a
**catalog-only** soft reset:

```bash
smith demo:reset
```

That truncates `tracks` → `albums` → `artists` and `notifications`, then
runs `db:seed` again. The `users` table is untouched, so existing cookie
sessions stay valid.

### In-process schedule

With `DEMO_SCHEDULE=1` (default in Docker), the entrypoint starts
`smith schedule:work` alongside the HTTP server. `routes/console.py` runs
`demo:reset` hourly while the process is awake.

### HTTP + GitHub Actions (Render Free)

Free instances sleep; the in-process scheduler may not fire. A bearer-token
endpoint and a scheduled workflow cover that:

| Piece | Detail |
| --- | --- |
| `POST /__orbit-demo/reset` | Header `Authorization: Bearer <DEMO_RESET_TOKEN>` |
| `GET /__orbit-demo/reset-status` | Whether a token is configured |
| Workflow | `.github/workflows/reset-demo.yml` (every 6h + manual) |

Repo secrets for the workflow:

- `DEMO_RESET_URL` — e.g. `https://your-service.onrender.com/__orbit-demo/reset`
- `DEMO_RESET_TOKEN` — same value as the Render env var `DEMO_RESET_TOKEN`
  (Blueprint generates one via `generateValue: true`)

## Deploy on Render (free)

Render Free can run this ASGI app. The SQLite file is **ephemeral** (lost on
spin-down, restart, and redeploy). That is intentional: the Docker entrypoint
always runs `smith migrate --force --seed`.

### Option A — Blueprint

1. Push this repo to GitHub.
2. Render Dashboard → **New** → **Blueprint** → select the repo.
3. Blueprint file: `examples/demo/render.yaml` (root / context = `examples/demo`).
4. Set `APP_URL` to the service URL once known.
5. Deploy. Health check: `/login`.
6. Copy `DEMO_RESET_TOKEN` from the Render dashboard into GitHub secrets
   (with `DEMO_RESET_URL`) if you want the catalog reset workflow.

### Option B — Web Service (Docker)

1. **New** → **Web Service** → connect the repo.
2. Root directory: `examples/demo`.
3. Dockerfile path: `Dockerfile` (relative to that root).
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
| `DEMO_SCHEDULE` | `1` (optional; start `schedule:work`) |
| `DEMO_RESET_TOKEN` | random secret for `POST /__orbit-demo/reset` |

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
4. Prefer migrate without re-seeding every boot, or keep `--seed` (seeders no-op when rows exist). Soft resets via `demo:reset` / the HTTP endpoint refresh the catalog without logging users out.

## Docker locally

From **`examples/demo`** (PyPI packages only):

```bash
cd examples/demo
docker build -t orbit-demo .
docker run --rm -p 8000:8000 \
  -e APP_KEY=base64:orbit-demo-local-dev-key-change-me \
  -e APP_URL=http://127.0.0.1:8000 \
  -e SESSION_SECURE_COOKIE=false \
  -e DEMO_RESET_TOKEN=local-dev-reset \
  orbit-demo
```

Or from the monorepo root:

```bash
docker build -f examples/demo/Dockerfile -t orbit-demo examples/demo
```

Soft reset while the container is up:

```bash
curl -X POST http://127.0.0.1:8000/__orbit-demo/reset \
  -H "Authorization: Bearer local-dev-reset"
```

## Seed data

Idempotent catalog seeder: **24 artists**, **~56 albums**, **~275 tracks**
(plus a few soft-deleted rows) spanning 2018–2025 with varied formats, markets,
genres, platforms, and play counts so every widget and chart type has real data.
Notification seeder adds welcome/tip rows for the demo admin.
