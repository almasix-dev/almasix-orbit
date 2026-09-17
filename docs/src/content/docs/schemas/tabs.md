---
title: Tabs
description: Tabbed schema layouts.
---

```python
from almasix.orbit.schemas import Tabs
from almasix.orbit.forms import TextInput

Tabs.make().tabs(
    ("Account", [TextInput.make("email")]),
    ("Profile", [TextInput.make("bio")]),
)
```

