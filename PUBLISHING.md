# Publishing almasix-orbit (PyPI)

Orbit is a monorepo. Docs are separate — see [CLOUDFLARE.md](./CLOUDFLARE.md).

## Why unique environments (not unique workflows)?

PyPI Trusted Publishing allows **one project** per:

`(GitHub owner, repository, workflow filename, environment)`

When `publish.yml` calls reusable jobs (or a matrix), GitHub **attestations**
record the **caller** workflow — always `publish.yml` — not any
`publish-almasix-orbit-*.yml` helper. Registering those helper filenames as
Trusted Publishers will fail with:

> Build Config URI …/publish.yml … does not match expected Trusted Publisher
> (publish-almasix-orbit-support.yml @ …)

So uniqueness comes from the **Environment name**. Workflow is always
`publish.yml`.

---

## Specific steps (one-time) — do this before the next release

### A. GitHub Environments

https://github.com/almasix-dev/almasix-orbit/settings/environments

Create **20** environments (no secrets):

**Production**

- `pypi-almasix-orbit-support`
- `pypi-almasix-orbit-schemas`
- `pypi-almasix-orbit-forms`
- `pypi-almasix-orbit-actions`
- `pypi-almasix-orbit-tables`
- `pypi-almasix-orbit-infolists`
- `pypi-almasix-orbit-notifications`
- `pypi-almasix-orbit-widgets`
- `pypi-almasix-orbit-query-builder`
- `pypi-almasix-orbit`

**TestPyPI**

- `testpypi-almasix-orbit-support`
- `testpypi-almasix-orbit-schemas`
- `testpypi-almasix-orbit-forms`
- `testpypi-almasix-orbit-actions`
- `testpypi-almasix-orbit-tables`
- `testpypi-almasix-orbit-infolists`
- `testpypi-almasix-orbit-notifications`
- `testpypi-almasix-orbit-widgets`
- `testpypi-almasix-orbit-query-builder`
- `testpypi-almasix-orbit`

You can delete old `pypi` / `testpypi` envs if unused.

### B. Fix PyPI pending / trusted publishers

1. Open each project (or Pending publishers) on https://pypi.org/
2. **Remove** any publisher that points at `publish-almasix-orbit-*.yml`
3. Add / update so **every** row uses Workflow `publish.yml` and a **unique** env:

| PyPI Project Name | Owner | Repository | Workflow name | Environment name |
|-------------------|-------|------------|---------------|------------------|
| `almasix-orbit-support` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit-support` |
| `almasix-orbit-schemas` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit-schemas` |
| `almasix-orbit-forms` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit-forms` |
| `almasix-orbit-actions` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit-actions` |
| `almasix-orbit-tables` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit-tables` |
| `almasix-orbit-infolists` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit-infolists` |
| `almasix-orbit-notifications` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit-notifications` |
| `almasix-orbit-widgets` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit-widgets` |
| `almasix-orbit-query-builder` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit-query-builder` |
| `almasix-orbit` | `almasix-dev` | `almasix-orbit` | `publish.yml` | `pypi-almasix-orbit` |

### C. TestPyPI

Same 10 rows on https://test.pypi.org/manage/account/publishing/ with
Environment = `testpypi-…` (same suffixes as above).

---

## Release flow

1. All `packages/*/pyproject.toml` versions match (e.g. `0.1.0`).
2. Merge publish fixes to `main`.
3. Tag + GitHub Release `vX.Y.Z` (or re-run Publish after fixing publishers).
4. Install: `pip install almasix-orbit==X.Y.Z`

### Rehearse

Actions → **Publish** → Run workflow → `testpypi`.

### Local build

```bash
pip install build twine
for pkg in support schemas forms actions tables infolists notifications widgets query-builder panels; do
  python -m build "packages/$pkg"
  twine check --strict "packages/$pkg/dist"/*
done
```
