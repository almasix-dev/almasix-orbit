---
title: Replicate action
description: ReplicateAction — duplicate a record with exclude attributes and replica lifecycle hooks.
---

## Introduction

`ReplicateAction` copies a record into a new one. Defaults: name `replicate`, label **Replicate**, plus icon, gray color.

```python title="app/orbit/resources/post_resource.py"
from almasix.orbit.actions import ReplicateAction

ReplicateAction.make()
    .exclude_attributes(["slug", "published_at"])
    .using(lambda replica, **_: Post.create(**replica))
    .success_notification("Replicated")
```

![Orbit ReplicateAction (light)](/examples/light/actions/replicate.png)

![Orbit ReplicateAction (dark)](/examples/dark/actions/replicate.png)

## Exclude attributes

`.exclude_attributes([...])` drops keys from the default replica (always excludes `id`). Works on dict records and simple objects with `__dict__`.

```python title="app/orbit/actions/replicate_exclude.py"
from almasix.orbit.actions import ReplicateAction

ReplicateAction.make().exclude_attributes(["slug", "views", "published_at"])
```

## Custom replica

`.replicate_using(callback)` replaces the default attribute copy. The callback receives the source `record` and must return the replica payload (dict or model — your `.using` / `.action` decides).

```python title="app/orbit/actions/replicate_using.py"
from almasix.orbit.actions import ReplicateAction

ReplicateAction.make().replicate_using(
    lambda record, **_: {**record, "title": f"{record['title']} (copy)", "status": "draft"}
)
```

## Replica lifecycle

Order inside `.call(record=...)`:

1. `.before`
2. Build replica (`.replicate_using` or default)
3. `.before_replica_saved`
4. `.using` / `.action` (kwargs include `record` + `replica`)
5. `.after_replica_saved`
6. `.after`

```python title="app/orbit/actions/replicate_hooks.py"
from almasix.orbit.actions import ReplicateAction

ReplicateAction.make()
    .before_replica_saved(lambda replica, **_: replica.update({"slug": unique_slug()}))
    .using(lambda replica, **_: Post.create(**replica))
    .after_replica_saved(lambda replica, **_: attach_default_tags(replica))
```

Halt / cancel from any hook stops the remaining chain.
