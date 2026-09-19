# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1 | Panel Configuration | `docs/src/content/docs/panels/configuration.md` | **closed** |
| 2 | Tables overview | `docs/src/content/docs/tables/overview.md` | **closed** |
| 3+ | Remaining Orbit doc features | docs nav | queued |

## Tables overview — gap matrix vs Filament 5

Reference: https://filamentphp.com/docs/5.x/tables/overview

### Done

| Filament | Orbit |
|----------|-------|
| `columns` / `pushColumns` | `.columns()` / `.push_columns()` |
| Dot relationship columns | `Column.resolve_state` via `dot_get` |
| `searchable` / `sortable` (columns) | present |
| Table `searchable` / `searchUsing` | `.searchable()` / `.search_using()` |
| `defaultSort` | `.default_sort()` |
| Filters + `deferFilters` | present |
| `recordActions` / `toolbarActions` | `.record_actions()` / `.toolbar_actions()` (+ existing names) |
| Pagination options / disable / extreme / modes | `.paginated()`, `.extreme_pagination_links()`, `.pagination_mode(PaginationMode)` |
| `queryStringIdentifier` / persist per-page | present |
| `recordUrl` / open in new tab | `.record_url()` / `.open_record_url_in_new_tab()` |
| `reorderable` + hooks | `.reorderable()`, `.apply_reorder()`, host `toggleReordering` |
| Heading / description / header | `.heading()` / `.description()` / `.header()` |
| `poll` / `deferLoading` | `.poll()` / `.defer_loading()` |
| `persistInSession` (+ individuals) | `.persist_in_session()` etc. |
| `striped` / `recordClasses` | present |
| Empty state icon / custom view | `.empty_state_icon()` / `.empty_state()` |
| `configureUsing` | `Table.configure_using()` |

### Deferred (later tracks)

| Filament | Reason |
|----------|--------|
| Full DnD reorder UX in orbit.js | Chrome + callbacks shipped; drag polish later |
| Column manager reorder (`reorderableColumns`) | Columns feature page |
| Filters layout enums | Filters overview feature |
| Scout-specific search | Covered by `.search_using()` |

## Close checklist (Tables overview)

- [x] Gap matrix accurate after implementation
- [x] orbit-admin sample exercises overview APIs (`TablesOverviewResource`)
- [x] Tests at 100% for touched Table/column surface
- [x] Docs updated (`tables/overview.md`)
- [x] Status → **closed**

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
