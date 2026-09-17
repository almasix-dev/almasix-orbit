---
title: Prime components
description: Text, Icon, Image, and UnorderedList primes.
---

```python
from almasix.orbit.schemas import Text, Icon, Image, UnorderedList

Text.make("Hello")
Icon.make("heroicon-o-home")
Image.make().url("/logo.png")
UnorderedList.make().items(["One", "Two"])
```

