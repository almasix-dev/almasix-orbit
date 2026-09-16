# Publishing almasix-orbit (PyPI)

Orbit is a monorepo. Docs (`orbit.almasix.com`) are **not** on PyPI — see
[CLOUDFLARE.md](./CLOUDFLARE.md).

## Why unique workflows?

PyPI Trusted Publishing allows **only one project** per:

`(GitHub owner, repository, workflow filename, environment)`

So we ship **one workflow file per package**. They all share Environment names
`pypi` / `testpypi`; uniqueness comes from the **workflow filename**.

| PyPI project | Workflow filename (register this) |
|--------------|-------------------------------------|
| `almasix-orbit-support` | `publish-almasix-orbit-support.yml` |
| `almasix-orbit-schemas` | `publish-almasix-orbit-schemas.yml` |
| `almasix-orbit-forms` | `publish-almasix-orbit-forms.yml` |
| `almasix-orbit-actions` | `publish-almasix-orbit-actions.yml` |
| `almasix-orbit-tables` | `publish-almasix-orbit-tables.yml` |
| `almasix-orbit-infolists` | `publish-almasix-orbit-infolists.yml` |
| `almasix-orbit-notifications` | `publish-almasix-orbit-notifications.yml` |
| `almasix-orbit-widgets` | `publish-almasix-orbit-widgets.yml` |
| `almasix-orbit-query-builder` | `publish-almasix-orbit-query-builder.yml` |
| `almasix-orbit` | `publish-almasix-orbit.yml` |

Orchestrator: [`publish.yml`](./.github/workflows/publish.yml) builds once, then
calls each of the files above. Do **not** register `publish.yml` or
`publish-build.yml` as publishers.

---

## Specific steps (one-time)

### A. GitHub Environments

On https://github.com/almasix-dev/almasix-orbit/settings/environments

1. Create environment **`pypi`**
2. Create environment **`testpypi`**
3. No secrets / vars required (OIDC only)

### B. PyPI pending publishers (production)

1. Log in to PyPI as the project owner.
2. Open https://pypi.org/manage/account/publishing/
3. Under **Pending publishers**, add **10 rows** — copy each line exactly:

| PyPI Project Name | Owner | Repository name | Workflow name | Environment name |
|-------------------|-------|-----------------|---------------|------------------|
| `almasix-orbit-support` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit-support.yml` | `pypi` |
| `almasix-orbit-schemas` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit-schemas.yml` | `pypi` |
| `almasix-orbit-forms` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit-forms.yml` | `pypi` |
| `almasix-orbit-actions` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit-actions.yml` | `pypi` |
| `almasix-orbit-tables` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit-tables.yml` | `pypi` |
| `almasix-orbit-infolists` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit-infolists.yml` | `pypi` |
| `almasix-orbit-notifications` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit-notifications.yml` | `pypi` |
| `almasix-orbit-widgets` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit-widgets.yml` | `pypi` |
| `almasix-orbit-query-builder` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit-query-builder.yml` | `pypi` |
| `almasix-orbit` | `almasix-dev` | `almasix-orbit` | `publish-almasix-orbit.yml` | `pypi` |

### C. TestPyPI pending publishers (rehearsal)

1. Open https://test.pypi.org/manage/account/publishing/
2. Add the **same 10 rows**, but Environment name = **`testpypi`**
   (workflow filenames unchanged).

### D. First publish creates the projects

Pending publishers become active when the matching workflow first uploads.
After that, manage each project under
`https://pypi.org/manage/project/<name>/settings/publishing/`.

---

## Every release

### 1. Sync versions

Every `packages/*/pyproject.toml` must share the same `version` (e.g. `0.1.0`).

```bash
# bump example → 0.1.1
for f in packages/*/pyproject.toml; do
  sed -i 's/^version = "0.1.0"/version = "0.1.1"/' "$f"
done
git add packages/*/pyproject.toml
git commit -m "chore: bump orbit packages to 0.1.1"
git push origin main
```

### 2. Rehearse on TestPyPI

1. Finish **§C** above.
2. GitHub → Actions → **Publish** → **Run workflow** → target **`testpypi`**.
3. Confirm all 10 package jobs are green.
4. Check https://test.pypi.org/project/almasix-orbit/

### 3. Production release

```bash
git tag -a v0.1.1 -m "almasix-orbit 0.1.1"
git push origin v0.1.1
```

Then GitHub → **Releases** → Draft release for that tag → **Publish release**.

That runs `publish.yml` → build → each `publish-almasix-orbit-*.yml` with
Environment `pypi`.

### 4. Install check

```bash
pip install almasix-orbit==0.1.1
python -c "from almasix.orbit import Panel; print(Panel.make('admin').id)"
```

---

## Local build (no upload)

```bash
pip install build twine
for pkg in support schemas forms actions tables infolists notifications widgets query-builder panels; do
  python -m build "packages/$pkg"
  twine check --strict "packages/$pkg/dist"/*
done
```

## Users install

```bash
pip install almasix-orbit
```
