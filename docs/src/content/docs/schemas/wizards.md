---
title: Wizards
description: Multi-step schema wizards.
---

```python
from almasix.orbit.schemas import Wizard
from almasix.orbit.forms import TextInput

Wizard.make().steps(
    ("Basics", [TextInput.make("title")]),
    ("Details", [TextInput.make("body")]),
)
```

