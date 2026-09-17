---
title: Empty states
description: Render empty-state messaging in schemas.
---

```python
from almasix.orbit.schemas import EmptyState

EmptyState.make().heading("No results").description("Try another filter.")
```


## Preview

![Empty state (light)](/examples/light/schemas/empty-state.png)

![Empty state (dark)](/examples/dark/schemas/empty-state.png)
