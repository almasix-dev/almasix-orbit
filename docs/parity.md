# Filament 5.x ↔ Orbit parity matrix

Orbit targets FilamentPHP **5.x** API familiarity on Almasix (Conduit + Alpine). Status values: **Done**, Partial, Planned.

## Packages

| Filament package | Orbit package | Status |
|------------------|---------------|--------|
| support | `almasix-orbit-support` | Done |
| schemas | `almasix-orbit-schemas` | Done |
| forms | `almasix-orbit-forms` | Done |
| tables | `almasix-orbit-tables` | Done |
| actions | `almasix-orbit-actions` | Done |
| infolists | `almasix-orbit-infolists` | Done |
| notifications | `almasix-orbit-notifications` | Done |
| widgets | `almasix-orbit-widgets` | Done |
| query-builder | `almasix-orbit-query-builder` | Done |
| panels | `almasix-orbit` (panels) | Done |

## Support

| Feature | Status |
|---------|--------|
| `Component` fluent base (`make`, label, hidden, visible, disabled, live, dehydrated, default, helper/hint) | Done |
| Colors (`Color`, `Colors`) | Done |
| Icons (Heroicons outline SVG) | Done |
| HTML helpers (`e`, `tag`) | Done |

## Schemas

| Feature | Status |
|---------|--------|
| `Schema` container (state, fill, dehydrate, columns, render) | Done |
| `Grid` | Done |
| `Section` (heading, description, collapsible) | Done |
| `Tabs` | Done |
| `Fieldset` | Done |
| `Wizard` | Done |

## Forms (field types)

| Field | Status |
|-------|--------|
| TextInput | Done |
| Textarea | Done |
| Select | Done |
| Checkbox | Done |
| Toggle | Done |
| Hidden | Done |
| Placeholder | Done |
| DatePicker | Done |
| DateTimePicker | Done |
| TimePicker | Done |
| FileUpload | Done |
| Radio | Done |
| CheckboxList | Done |
| TagsInput | Done |
| ColorPicker | Done |
| RichEditor | Done |
| MarkdownEditor | Done |
| KeyValue | Done |
| Repeater | Done |
| Builder | Done |
| Slider | Done |
| ToggleButtons | Done |
| CodeEditor | Done |
| MultiSelect | Done |
| OneTimeCodeInput | Done |
| ViewField | Done |
| MorphToSelect | Done |
| TableSelect | Done |
| ModalTableSelect | Done |
| RelationshipRepeater | Done |
| Form validation (`required`, `email`, `numeric`, `integer`, `url`, `min`/`max`) | Done |

## Tables

| Feature | Status |
|---------|--------|
| Table (search, sort, paginate, striped, empty state, render) | Done |
| TextColumn / BadgeColumn / BooleanColumn / IconColumn / ImageColumn / ColorColumn | Done |
| TagsColumn / SelectColumn / CheckboxColumn / TextInputColumn / ToggleColumn / ViewColumn | Done |
| ColumnGroup | Done |
| Filters (`Filter`, `SelectFilter`, `TernaryFilter`, `FilterGroup`) | Done |
| Row / bulk / header actions | Done |

## Actions

| Feature | Status |
|---------|--------|
| Action (authorize, call, form modal, confirmation, render) | Done |
| CreateAction / EditAction / ViewAction / DeleteAction / DeleteBulkAction | Done |

## Infolists

| Feature | Status |
|---------|--------|
| Infolist render | Done |
| TextEntry / IconEntry / ImageEntry / ColorEntry / CodeEntry / KeyValueEntry / RepeatableEntry | Done |

## Notifications

| Feature | Status |
|---------|--------|
| Notification (success/danger/warning/info) | Done |
| Channels: flash / database / broadcast | Done |
| Notifier bag + flash render | Done |

## Widgets

| Feature | Status |
|---------|--------|
| StatsOverviewWidget + Stat | Done |
| ChartWidget | Done |
| TableWidget | Done |

## Query builder

| Feature | Status |
|---------|--------|
| Constraints (text/select/boolean/date/number) | Done |
| Operators + `QueryBuilder.apply` | Done |

## Panels / resources / pages / relation managers

| Feature | Status |
|---------|--------|
| Panel (brand, colors, nav, middleware, discover, render_shell) | Done |
| PanelRegistry | Done |
| Resource (form/table/infolist, permissions, pages map) | Done |
| Page | Done |
| RelationManager | Done |
| LiveResource test helper | Done |
| `make:orbit-resource` command stub | Done |
