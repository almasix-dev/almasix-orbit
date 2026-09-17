---
title: Sections
description: Group schema components in a Section.
---

```python
from almasix.orbit.schemas import Section
from almasix.orbit.forms import TextInput

Section.make("profile")
    .heading("Profile")
    .description("Public details")
    .schema([
        TextInput.make("name").required(),
    ])
```

See [Schemas overview](/schemas/overview/).

## Preview

![Orbit schemas/section (light)](/examples/light/schemas/section.png)

![Orbit schemas/section (dark)](/examples/dark/schemas/section.png)
