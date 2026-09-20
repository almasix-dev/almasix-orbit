---
title: Packages
description: Orbit’s PyPI packages and import map.
---

Install the meta-package and you get the whole family. Imports always live under `almasix.orbit…` thanks to `pkgutil.extend_path`.

```bash title="terminal"
pip install almasix-orbit
```

Each package is also installable on its own when you only need forms, tables, or the support toolkit inside a non-panel app.

## Map

| PyPI package | Import | Role |
|--------------|--------|------|
| `almasix-orbit` | `almasix.orbit` / `almasix.orbit.panels` | Panels, resources, pages, relation managers, provider, `LiveResource` |
| `almasix-orbit-support` | `almasix.orbit.support` | Component, colors, icons, HTML, `evaluate` |
| `almasix-orbit-schemas` | `almasix.orbit.schemas` | Schema + layouts |
| `almasix-orbit-forms` | `almasix.orbit.forms` | Form + fields |
| `almasix-orbit-tables` | `almasix.orbit.tables` | Table, columns, filters |
| `almasix-orbit-actions` | `almasix.orbit.actions` | Actions + CRUD presets |
| `almasix-orbit-infolists` | `almasix.orbit.infolists` | Infolist + entries |
| `almasix-orbit-notifications` | `almasix.orbit.notifications` | Notification + Notifier + stores |
| `almasix-orbit-widgets` | `almasix.orbit.widgets` | Stats, charts, table widgets |
| `almasix-orbit-query-builder` | `almasix.orbit.query_builder` | Constraints + apply |

## Prefer these imports

```python
from almasix.orbit import Panel, PanelRegistry, Resource, Page, RelationManager
from almasix.orbit.forms import Form, TextInput
from almasix.orbit.tables import Table, TextColumn
from almasix.orbit.actions import CreateAction, EditAction, DeleteAction
from almasix.orbit.infolists import Infolist, TextEntry
from almasix.orbit.schemas import Section, Grid, Tabs
from almasix.orbit.notifications import Notification, Notifier, get_notifier
from almasix.orbit.widgets import StatsOverviewWidget
from almasix.orbit.query_builder import QueryBuilder, TextConstraint
from almasix.orbit.support import Color, icon, evaluate, HtmlString
from almasix.orbit.testing import LiveResource
```

`LiveResource` lives in the panels package and is imported from `almasix.orbit.testing` — see [Testing](/testing/overview/). Support helpers are documented in [Support](/support/overview/).

## Community plugins

Third-party packages register with `.plugin(...)` on a panel. Browse published listings on the [plugin marketplace](/plugins/), install from [Using a plugin](/plugins/using/), or publish your own via [Get listed](/plugins/get-listed/).

## Dependencies

Orbit expects **Almasix**, **Conduit**, and **permission** in the app environment. See [Installation](/getting-started/installation/).
