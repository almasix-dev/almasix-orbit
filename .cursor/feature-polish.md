# Feature polish tracker

Process: see [`.cursor/rules/feature-polish.mdc`](rules/feature-polish.mdc).

## Queue

| Order | Feature | Docs | Status |
|------:|---------|------|--------|
| 1–17 | Panel / Tables / Columns / Filters | (prior) | **closed** |
| 18–30 | Schemas module | `docs/src/content/docs/schemas/*` | **closed** |
| 31–65 | Forms module | `docs/src/content/docs/forms/*` | **closed** |
| 66+ | Remaining Orbit doc features | docs nav | queued |

## Forms — closed

**Bar met:** Filament 5–equivalent Field chrome + validation fluent APIs, Filament-depth docs (explanation + code + light/dark screenshots per subsection), gallery variants + captures, 100% test coverage.

### Shared Field APIs shipped

Content slots, `trim` / `strip_characters` / `length` / `tel_regex` / `autocapitalize`, `mark_as_required`, `disabled_on` / `hidden_on` / `visible_on`, validation fluent helpers, Select `boolean` / `disable_option_when` / `preload` / `wrap`, Toggle `on_color` / `off_color` / icons / `inline`.

### Honest stubs (documented)

TableSelect / ModalTableSelect (Select-based chrome), CodeEditor / MarkdownEditor (textarea chrome until Monaco/CodeMirror).
