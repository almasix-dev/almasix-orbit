# Orbit Admin (Almasix + Conduit)

Canonical demo for Orbit panels. Treat this like a real Almasix app that depends
on local `almasix-orbit` (not ten editable package roots).

## Setup (pip — works without uv)

Requires a sibling Almasix checkout at `../almasix` (i.e. `Projects/almasix` next to `Projects/almasix-orbit`).

```bash
cd examples/orbit-admin
./scripts/bootstrap.sh
source .venv/bin/activate
smith serve
```

Open [http://127.0.0.1:3000/admin](http://127.0.0.1:3000/admin).

**PyCharm:** open `examples/orbit-admin` as the project, interpreter =
`examples/orbit-admin/.venv`. Bootstrap symlinks `orbit` into your local
Almasix package (`../almasix/src/almasix/orbit` → combined tree) so
`from almasix.orbit` resolves like a normal subpackage. If imports stay red:
File → Invalidate Caches → Invalidate and Restart.

Navigation layout is set on the panel (not via query params):

```python
Panel.make("admin").apps_navigation()      # sidebar roots + topbar (default)
# .sidebar_navigation()                    # full tree in sidebar
# .top_navigation()                        # topbar only
# .navigation_layout("apps")               # same as apps_navigation()
```

**Auth user (database):**

```bash
smith migrate
smith orbit:user
# or non-interactive:
smith orbit:user --name="Ada" --email="ada@orbit.test" --password="secret"
```

Fresh apps without a User model: `smith orbit:user --scaffold`, then migrate, then create.

Local demos can still use a panel principal (no DB session) with `.default_user()` / `.user(OrbitUser…)`:

```python
Panel.make("admin").login().default_user()
# or:
Panel.make("admin").login().user(
    OrbitUser.make().name("Ada").email("ada@orbit.test").admin()
)
```

### What went wrong with a plain venv?

`pip install almasix-orbit` from **PyPI** pulls published wheels that may lag this
branch. Point the dependency at `packages/combined` (see `scripts/bootstrap.sh` /
`[tool.uv.sources]`) so you get the local tree in one editable install.

If you use uv instead:

```bash
uv sync   # respects [tool.uv.sources] → packages/combined
smith serve
```
