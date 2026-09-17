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

## Preview

![Orbit schemas/wizard (light)](/examples/light/schemas/wizard.png)

![Orbit schemas/wizard (dark)](/examples/dark/schemas/wizard.png)
