---
title: Modals
description: Modal and slide-over action dialogs.
---

```python
from almasix.orbit.actions import Action

Action.make("edit").slide_over().modal_width("2xl").requires_confirmation()
```

