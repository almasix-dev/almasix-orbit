# almasix-orbit

<p align="center">
  <a href="https://pypi.org/project/almasix-orbit/"><img alt="PyPI" src="https://img.shields.io/pypi/v/almasix-orbit?style=for-the-badge&label=pypi&color=4c1d95&v=0.3.1"></a>
  <a href="https://github.com/almasix-dev/almasix-orbit/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/almasix-dev/almasix-orbit/ci.yml?branch=main&style=for-the-badge&label=CI&logo=githubactions&logoColor=white"></a>
  <a href="https://github.com/almasix-dev/almasix-orbit/tree/main/tests"><img alt="coverage" src="https://img.shields.io/badge/coverage-100%25-31c48d?style=for-the-badge&logo=codecov&logoColor=white"></a>
  <a href="https://pypi.org/project/almasix/"><img alt="Almasix &gt;=0.6.0" src="assets/almasix-version-badge.svg" height="28"></a>
  <a href="https://github.com/almasix-dev/almasix-orbit/blob/main/LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge"></a>
</p>

**Orbit** — server-driven admin UI for [Almasix](https://github.com/almasix-dev/almasix).

Panels, resources, forms, tables, actions, infolists, notifications, widgets, and
query builder — on **Conduit** + **Alpine.js**, with semantic `.or-*` CSS.

Inspired by [Filament](https://filamentphp.com/); built for the Almasix/Python world.

Docs: [orbit.almasix.com](https://orbit.almasix.com/).

Install as `almasix.orbit`:

```bash
pip install almasix-orbit
```

Requires `almasix`, `almasix-conduit`, and `almasix-permission`.

```python
from almasix.orbit import Panel, Resource
```

## Install (editable)

Split packages use `pkgutil.extend_path`, which confuses PyCharm. For a real app
against this checkout, depend on the **combined** tree (one editable root — same
layout as a PyPI install):

```bash
cd examples/orbit-admin
./scripts/bootstrap.sh   # pip install -e ../../packages/combined
```

Or in your app’s `pyproject.toml`:

```toml
dependencies = ["almasix-orbit"]

[tool.uv.sources]
almasix-orbit = { path = "../almasix-orbit/packages/combined", editable = true }
```

Open that **app** project in PyCharm and select its `.venv`. No extra source roots.

## Quick start

```python
from almasix.orbit import Panel, Resource

panel = (
    Panel.make("admin")
    .path("admin")
    .brand_name("Orbit")
    .login()
    .resources([PostResource])
)
```

See `examples/orbit-admin` for a full Almasix app (`./scripts/bootstrap.sh` then `smith serve`).

## Demo

Public music-catalog sample (Artists + Albums) lives in [`examples/demo`](examples/demo).
It targets **Render Free** + SQLite with **intentional reseed on boot**, and depends
on **PyPI** releases of Almasix / Orbit / Conduit (not editable checkouts). Kitchen-sink
remains [`examples/orbit-admin`](examples/orbit-admin).

```bash
cd examples/demo
./scripts/bootstrap.sh && source .venv/bin/activate
smith migrate --seed && smith serve
# login: demo@orbit.test / secret
```

Deploy notes: [`examples/demo/README.md`](examples/demo/README.md) (`render.yaml` + Dockerfile).

## Packages

| Package | Import |
| --- | --- |
| `almasix-orbit` | `almasix.orbit` (panels / meta) |
| `almasix-orbit-support` | `almasix.orbit.support` |
| `almasix-orbit-schemas` | `almasix.orbit.schemas` |
| `almasix-orbit-forms` | `almasix.orbit.forms` |
| `almasix-orbit-tables` | `almasix.orbit.tables` |
| `almasix-orbit-actions` | `almasix.orbit.actions` |
| `almasix-orbit-infolists` | `almasix.orbit.infolists` |
| `almasix-orbit-notifications` | `almasix.orbit.notifications` |
| `almasix-orbit-widgets` | `almasix.orbit.widgets` |
| `almasix-orbit-query-builder` | `almasix.orbit.query_builder` |

## Features

- Multi-panel admin shells with navigation, branding, auth, and tenancy hooks
- Resources with list / create / edit / view pages on Conduit hosts
- Fluent forms, schemas, tables, actions, infolists, notifications, and widgets
- ORM-backed CRUD plus demo seed resources
- Query builder helpers and semantic `.or-*` CSS / Alpine UI

## Tests

```bash
pytest tests --cov=almasix.orbit --cov-branch
```

Aim for **100%** statement + branch coverage. CI fails under **99.5%**
(`pyproject.toml` / `.github/workflows/ci.yml`).

## Discovery

```toml
[project.entry-points."almasix.providers"]
orbit = "almasix.orbit.provider:OrbitServiceProvider"
```

Or list the provider explicitly in `config/app.py`.

## Maintainer notes

- Feature checklist for contributors: [docs/parity.md](docs/parity.md)
- PyPI: [PUBLISHING.md](./PUBLISHING.md)
- Docs / Cloudflare: [CLOUDFLARE.md](./CLOUDFLARE.md)
