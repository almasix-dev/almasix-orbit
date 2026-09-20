---
title: Configuration & assets
description: Panel config defaults, published CSS/JS, Prism directives, and where SPA, billing, and notifications plug in.
---

Orbit configures itself lightly and lets the `Panel` instance carry brand and path. Assets are optional publishes. Full fluent surface: [Panel configuration](/panels/configuration/).

## Provider defaults

When `OrbitServiceProvider` registers, it seeds config if missing:

```python
{
    "path": "/orbit",
    "font": "Outfit",
    "brand": "Orbit",
}
```

Prefer setting these on the panel — that’s the source of truth for the shell:

```python title="app/orbit/admin/panel.py"
Panel.make("admin")
    .path("orbit")
    .brand_name("Acme Admin")
    .font("Outfit")
    .primary("#f1511b")
```

There is no published `config/orbit.py` file. When you need app-wide knobs, set `app.config["orbit"] = {…}` before boot or extend the provider.

![Orbit panel shell (light)](/examples/light/configuration/shell.png)

![Orbit panel shell (dark)](/examples/dark/configuration/shell.png)

## Assets

| Source | Published path | Shell URL |
|--------|----------------|-----------|
| `orbit.css` | `public/vendor/orbit/orbit.css` | `/vendor/orbit/orbit.css` |
| `orbit.js` | `public/vendor/orbit/orbit.js` | `/vendor/orbit/orbit.js` |

```bash title="terminal"
smith vendor:publish --tag=orbit-assets
```

`orbit.js` registers Alpine data for toasts, the database bell, live polling, SPA navigation, and action modals. After you change vendor files, republish or copy from the package so the panel shell picks them up.

![Orbit published assets in the shell (light)](/examples/light/configuration/assets.png)

![Orbit published assets in the shell (dark)](/examples/dark/configuration/assets.png)

## Prism directives

If Prism’s engine is bound, these directives are available:

```html
@orbitStyles
@orbitScripts
```

They populate `__orbit_styles` and `__orbit_scripts` in the view context. The panel shell links the vendor URLs directly; use the directives when you embed Orbit chrome in your own layouts.

## Middleware & auth

Panels default to the Almasix `web` middleware group (session, CSRF, cookies). Extra middleware **appends**:

```python
panel.middleware(["auth"]).login().auth_guard("web")
# → ["web", "auth"]
```

Use `.middleware([...], replace=True)` only when you need to replace the whole stack. Orbit still gates guests via `.login()` — prefer not putting Almasix `auth` on the panel if you want the Orbit login page to stay reachable. Resource abilities still go through `can_*` helpers — see [Resources](/resources/overview/).

## SPA, billing, and notifications

These are panel methods, not separate config files:

| Method | Docs |
|--------|------|
| `.spa()` / `.spa_url_exceptions()` | [Panel configuration](/panels/configuration/) — fetch-and-swap of `main.or-content` |
| `.tenant_billing(True)` / `.billing_provider(...)` | [Multi-tenancy](/users/tenancy/) — `ManageBilling` + a `BillingProvider` |
| `.sqlite_notifications()` / `.live_broadcasts()` | [Database](/notifications/database-notifications/) and [broadcast](/notifications/broadcast-notifications/) |

`PanelRegistry.get_by_path(...)` and `.get_by_domain(...)` look up a registered panel when one app hosts several.

## Scaffolding

```bash title="terminal"
smith make:orbit-resource Post --panel=admin
smith make:orbit-resource Post --panel=admin --model=Post --generate
```

The command writes `app/orbit/{panel}/resources/post_resource.py`. `--generate` reflects the model’s table columns into form fields and table columns. `--force` overwrites an existing file. See [Resources overview](/resources/overview/#scaffolding-makeorbit-resource).
