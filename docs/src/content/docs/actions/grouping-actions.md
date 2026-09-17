---
title: Grouping actions
description: Group actions in dropdowns and button groups.
---

```python
from almasix.orbit.actions import ActionGroup, EditAction, DeleteAction

ActionGroup.make([EditAction.make(), DeleteAction.make()]).label("More")
```

