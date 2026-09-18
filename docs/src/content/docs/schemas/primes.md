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



## Preview

![Orbit schemas/primes-all (light)](/examples/light/schemas/primes-all.png)

![Orbit schemas/primes-all (dark)](/examples/dark/schemas/primes-all.png)
