---
title: Resource page hosts
description: List, Create, Edit, and View pages with tabs and forms that actually render.
---

Orbit ships page hosts that turn a Resource into HTML you can mount under Conduit:

```python
from almasix.orbit.panels.pages import ListRecords, CreateRecord, EditRecord, ViewRecord, Tab

class PostList(ListRecords):
    resource = PostResource

    @classmethod
    def get_tabs(cls):
        return [
            Tab("all").label("All"),
            Tab("published").label("Published").badge(3).modify_query_using(
                lambda rows: [r for r in rows if r.get("published")]
            ),
        ]

html = PostList.render(records=posts, active_tab="published")
html = CreateRecord  # bind resource similarly
```

`make:orbit-resource` now writes a Python stub file. Call `panel.discover_resources(...).load_discovered()` to import modules under a path.
