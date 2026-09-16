# Publishing almasix-orbit (PyPI)

Orbit is a **monorepo**. One GitHub Release (`vX.Y.Z`) publishes **all** packages
to PyPI via Trusted Publishing (OIDC). Docs (`orbit.almasix.com`) are **not** on
PyPI — see [CLOUDFLARE.md](./CLOUDFLARE.md).

## Packages (same version)

| PyPI name | Path |
|-----------|------|
| `almasix-orbit-support` | `packages/support` |
| `almasix-orbit-schemas` | `packages/schemas` |
| `almasix-orbit-forms` | `packages/forms` |
| `almasix-orbit-actions` | `packages/actions` |
| `almasix-orbit-tables` | `packages/tables` |
| `almasix-orbit-infolists` | `packages/infolists` |
| `almasix-orbit-notifications` | `packages/notifications` |
| `almasix-orbit-widgets` | `packages/widgets` |
| `almasix-orbit-query-builder` | `packages/query-builder` |
| `almasix-orbit` | `packages/panels` (meta / panels) |

Users normally install:

```bash
pip install almasix-orbit
```

That pulls the panel meta package and its Orbit dependencies (plus `almasix`,
`almasix-conduit`, `almasix-permission`).

## One-time: Trusted Publishing

While logged in as the PyPI owner, open
https://pypi.org/manage/account/publishing/ and add a **Pending publisher** for
**each** project name above:

| Field | Value |
|-------|-------|
| PyPI Project Name | *(each name in the table)* |
| Owner | `almasix-dev` |
| Repository name | `almasix-orbit` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

Optionally repeat on https://test.pypi.org/manage/account/publishing/ with
Environment `testpypi`.

Also create GitHub Environments **`pypi`** and **`testpypi`** on
`almasix-dev/almasix-orbit` (Settings → Environments). No secrets needed for OIDC.

## Bump version

Keep **every** `packages/*/pyproject.toml` `version` in sync (e.g. `0.1.0`).

```bash
# example: bump all to 0.1.1
for f in packages/*/pyproject.toml; do
  sed -i 's/^version = "0.1.0"/version = "0.1.1"/' "$f"
done
```

Commit, then tag:

```bash
git tag -a v0.1.1 -m "almasix-orbit 0.1.1"
git push origin v0.1.1
```

## Publish

1. **Rehearse (TestPyPI):** Actions → **Publish** → Run workflow → `testpypi`.
2. **Production:** GitHub → **Releases** → Draft a new release on tag `vX.Y.Z`
   (must match the packaged version). Publishing the release runs
   [`.github/workflows/publish.yml`](./.github/workflows/publish.yml).

## Install check

```bash
pip install almasix-orbit==0.1.0
python -c "from almasix.orbit import Panel; print(Panel.make('admin').to_dict())"
```

## Local build (no upload)

```bash
pip install build twine
for pkg in support schemas forms actions tables infolists notifications widgets query-builder panels; do
  python -m build "packages/$pkg"
  twine check --strict "packages/$pkg/dist"/*
done
```
