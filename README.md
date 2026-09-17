# almasix-orbit

**Orbit** — server-driven admin UI for Almasix.

Panels, resources, forms, tables, actions, infolists, notifications, widgets, and
query builder — on **Conduit** + **Alpine.js**, with semantic `.or-*` CSS.

Inspired by [Filament](https://filamentphp.com/); built for the Almasix/Python world.

## Install

```bash
pip install almasix-orbit
```

Requires `almasix`, `almasix-conduit`, and `almasix-permission`.

### Local app development (IDE-friendly)

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

## Packages

| Package | Import |
|---------|--------|
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

## Docs

https://orbit.almasix.com/

## Maintainer notes

- Feature checklist for contributors: [docs/parity.md](docs/parity.md)
- PyPI: [PUBLISHING.md](./PUBLISHING.md)
- Docs / Cloudflare: [CLOUDFLARE.md](./CLOUDFLARE.md)
