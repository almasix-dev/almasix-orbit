---
title: Configuration & assets
description: Panel config defaults, published CSS/JS, and Prism directives.
---

Orbit configures itself lightly and lets the `Panel` instance carry brand and path. Assets are optional publishes.

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

```python
Panel.make("admin")
    .path("orbit")
    .brand_name("Acme Admin")
    .font("Outfit")
    .colors(primary="#f1511b")
```

There is no published `config/orbit.py` file yet. When you need app-wide knobs, set `app.config["orbit"] = {…}` before boot or extend the provider.

## Assets

| Source | Published path | Shell URL |
|--------|----------------|-----------|
| `orbit.css` | `public/vendor/orbit/orbit.css` | `/vendor/orbit/orbit.css` |
| `orbit.js` | `public/vendor/orbit/orbit.js` | `/vendor/orbit/orbit.js` |

```bash title="terminal"
smith vendor:publish --tag=orbit-assets
```

`orbit.js` registers Alpine `orbitNotifications` data for flash rendering.

## Prism directives

If Prism’s engine is bound, these directives are available:

```html
@orbitStyles
@orbitScripts
```

They populate `__orbit_styles` and `__orbit_scripts` in the view context. The panel shell links the vendor URLs directly; use the directives when you embed Orbit chrome in your own layouts.

## Middleware & auth

```python
panel.middleware(["auth", "permission"]).login().auth_guard("web")
```

Defaults assume Almasix auth + permission middleware. Swap the list for your stack. Resource abilities still go through `can_*` helpers — see [Resources](/resources/overview/).

## Scaffolding

```bash title="terminal"
smith make:orbit-resource Post
```

The command is registered and accepts a name. File generation is still catching up — for now, copy the [quick start](/getting-started/quick-start/) resource and rename.
