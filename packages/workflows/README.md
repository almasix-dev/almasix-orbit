# almasix-orbit-workflows

Optional Orbit plugin for versioned workflows: forms, approvals, parallel branches, escalation, guest steps, and in-panel signatures.

The published document is the contract. A running case pins that version. Status labels live on the document, not in the engine.

```python
from almasix.orbit.workflows import WorkflowPlugin, role, starter

panel.plugin(WorkflowPlugin.make())
```

See `examples.py` for a contract flow (parallel review, escalation, signature) and the docs page `workflows/overview`.
