# Orbit Demo — music catalog

Slim public demo of [Orbit](https://orbit.almasix.com/) on Almasix + Conduit +
**SQLite**. Catalog resources: **Artists** and **Albums** (Tracks later).

Uses **production PyPI** releases of `almasix`, `almasix-orbit`, and
`almasix-conduit` (local and Render). Leave [`../orbit-admin`](../orbit-admin)
as the kitchen-sink playground against editable checkouts.

## Local setup

```bash
cd examples/demo
./scripts/bootstrap.sh
source .venv/bin/activate
smith migrate --seed
smith serve
```

Open the printed URL (panel is mounted at `/`).

**Demo login:** `demo@orbit.test` / `secret`

## Deploy on Render (free)

Render Free can run this ASGI app. The SQLite file is **ephemeral** (lost on
spin-down, restart, and redeploy). That is intentional for a public demo: the
Docker entrypoint always runs `smith migrate --force --seed`, so the catalog and
demo user reset to a clean seed on every cold start.

### Option A — Blueprint

1. Push this repo to GitHub.
2. Render Dashboard → **New** → **Blueprint** → select the repo.
3. Root / blueprint file: `examples/demo/render.yaml`.
4. Set `APP_URL` to the service URL once known (or leave and update later).
5. Deploy. Health check: `/login`.

### Option B — Web Service (Docker)

1. **New** → **Web Service** → connect the repo.
2. Root directory: `examples/demo`.
3. Runtime: **Docker**.
4. Instance: **Free**.
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

Render sets `PORT`; the entrypoint honours it.

### Durable SQLite (optional, paid)

Free cannot attach disks. For data that survives deploys:

1. Upgrade the service to **Starter** (~$7/mo).
2. Attach a **persistent disk** (~$0.25/GB/mo) mounted at `/app/database`.
3. Keep `DB_DATABASE=/app/database/database.sqlite`.
4. Prefer migrate without re-seeding on every boot (adjust entrypoint once the
   volume exists), or keep `--seed` — seeders no-op when rows already exist.

## Docker locally

```bash
cd examples/demo
docker build -t orbit-demo .
docker run --rm -p 8000:8000 \
  -e APP_KEY=base64:orbit-demo-local-dev-key-change-me \
  -e APP_URL=http://127.0.0.1:8000 \
  -e SESSION_SECURE_COOKIE=false \
  orbit-demo
```

## Next iterations

- Tracks resource
- Richer forms / filters / relation managers
- Custom domain + durable disk if the demo should keep edits
