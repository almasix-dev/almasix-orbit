# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1 | Panel Configuration | `docs/src/content/docs/panels/configuration.md` | **closed** |
| 2+ | Remaining Orbit doc features | docs nav | queued (pick next when starting) |

## Panel Configuration — gap matrix vs Filament 5

Reference: https://filamentphp.com/docs/5.x/panel-configuration (+ styling/auth configured on the panel).

### Done

| Area | Orbit API |
|------|-----------|
| Identity | `Panel.make(id)`, `.path()`, `.default()`, `.domain()`, `.home_url()`, `.favicon()` |
| Multi-panel | `PanelRegistry.register` / `.get` / `.all` / `.default` / `.get_default` |
| Brand | `.brand_name`, `.brand_logo`, `.brand_logo_dark`, `.brand_logo_only`, `.brand_name_font_size`, `.brand_logo_height` |
| Theme colors / font | `.font`, `.primary`, `.colors`, `.content_max_width`, `.simple_page_max_content_width` |
| Dark mode | `.dark_mode()`, `.theme_switcher()`, `.default_theme_mode()` |
| Contents | `.resources` / `.pages` / `.widgets`, `.discover_*`, `.load_discovered` |
| Auth pages | `.login` / `.signup` / `.dashboard` / `.auth_guard` |
| Middleware | `.middleware(..., replace=)`, `.auth_middleware(...)` |
| Nav chrome (basics) | `.navigation_layout`, `.apps_navigation`, `.sidebar_navigation`, `.top_navigation`, `.sidebar_collapsible`, groups/items, `.breadcrumbs_enabled` |
| Plugins / hooks | `.plugin` / `.plugins` (callable or `Plugin`), `.boot_using`, `.render_hook`, `.run_plugins` |
| Shell | `.render_shell`, breadcrumbs |

### Deferred (later features)

| Filament | Reason |
|----------|--------|
| `spa()` / prefetch / URL exceptions | SPA feature track |
| `unsavedChangesAlerts()` | Forms/actions UX track |
| `databaseTransactions()` | Actions/resources track |
| `assets([...])` | Asset pipeline track |
| `strictAuthorization()` | Auth/policies track |
| Error notification customization | Notifications track |
| `broadcasting(false)` | Realtime track |
| Multi-tenancy / MFA / clusters / global search depth | Separate doc tracks |
| `subNavigationPosition` | Navigation feature |
| Vite theme / custom Livewire chrome | Styling / host adapters |

## Close checklist (Panel Configuration)

- [x] Gap matrix accurate after implementation
- [x] orbit-admin sample exercises Panel Configuration
- [x] Tests at 100% for Panel configuration surface (`panel.py`)
- [x] Docs + screenshots updated
- [x] Status → **closed**
