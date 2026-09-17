---
title: Query builder
description: Constraint-based filtering for in-memory record lists.
---

The **query builder** lets users (or you) describe filters as constraints + operators, then apply them to a list of records.

```python
from almasix.orbit.query_builder import (
    QueryBuilder,
    TextConstraint,
    SelectConstraint,
    BooleanConstraint,
    DateConstraint,
    NumberConstraint,
)

qb = (
    QueryBuilder.make()
    .constraints([
        TextConstraint.make("title"),
        SelectConstraint.make("status").options({
            "draft": "Draft",
            "published": "Published",
        }),
        BooleanConstraint.make("featured"),
        DateConstraint.make("published_at"),
        NumberConstraint.make("views"),
    ])
    .rules([
        {"constraint": "title", "operator": "contains", "value": "orbit"},
        {"constraint": "status", "operator": "equals", "value": "published"},
    ])
)

filtered = qb.apply(posts)
```

## Operators

| Operator | Meaning |
|----------|---------|
| `equals` / `not_equals` | Equality |
| `contains` / `starts_with` / `ends_with` | String matching |
| `greater_than` / `less_than` | Ordering |
| `is_set` / `is_not_set` | Presence |
| `in` | Membership |

## Constraints

| Class | Typical use |
|-------|-------------|
| `TextConstraint` | Free text fields |
| `SelectConstraint` | Enumerated options |
| `BooleanConstraint` | True / false |
| `DateConstraint` | Dates |
| `NumberConstraint` | Numeric fields |

`Constraint` and `Operator` are available if you’re extending the set.

## Scope

`apply()` works on **in-memory** lists of dicts or objects — not ORM query objects. For Articulate queries, translate the same rules into builder calls in your app layer, or filter the page of records you already loaded.

Handy next to [table filters](/tables/) when you want a richer rule UI than a single select.
