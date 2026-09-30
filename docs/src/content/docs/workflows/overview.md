---
title: Workflows
description: Versioned processes for forms, approvals, parallel work, escalation, and signatures.
---

A workflow is a published document. A case follows one version of that document until it finishes. The words for each status — and whether that status finishes the case — are written on the document, so a leave request and a contract do not share a vocabulary.

Install the plugin and mount it on the panel:

```python title="app/orbit/panel.py"
from almasix.orbit import Panel
from almasix.orbit.workflows import WorkflowPlugin

Panel.make("admin").plugin(WorkflowPlugin.make())
```

## A contract

```python title="app/orbit/workflows/contract.py"
from almasix.orbit.workflows import Step, Workflow, role, starter

Workflow.make("contract").titled("Contract").status("draft", "Draft").status("review", "In review", color="warning").status("executed", "Executed", color="success", terminal=True).step(Step.make("draft", "form").assignee(starter()).schema([{"type": "TextInput", "name": "client", "label": "Client", "required": True}]).on("submit", to="legal", status="review", label="Submit")).step(Step.make("legal", "approval").assignee(role("legal")).on("approve", to="end", status="executed", label="Approve"))
```

`engine.save(contract.document())` keeps a draft. `engine.publish("contract")` checks the graph and freezes a version. `engine.start("contract", person)` opens a case on that version. A later publish does not move cases that already started.

## What a step can be

- **form**, **approval**, and **sign** open a task. The schema is a normal Orbit tree: grids, sections, tabs, wizards, and every form input, including `SignatureInput`.
- **route** chooses an edge from a condition such as `answers.amount>=1000` or `effect:seats_remaining`.
- **notify** sends a notice and follows its one edge.
- **fork** opens every outgoing branch at once. **join** waits for `all`, `any`, or a quorum.

An edge either **finishes** its branch (the others keep going) or **aborts** the fork (the others stop). Staff clearance finishes each department. A contract send-back aborts the other review.

## People

A step's assignees can be specific users, a role, the person who started the case, someone named in an earlier answer, a small expression (`manager_of:starter`, `role_except_starter:legal`), or a guest email. A guest receives a link that opens that step only. The link stops working when the task is finished or reassigned.

When several people qualify, the step says whether any one of them, all of them, or a quorum must finish it. A role task stays shared until someone claims it.

## Time, effects, and signatures

`escalate(after="2d", ...)` moves the case along an edge when the deadline passes, in the document's timezone. `remind("1d")` nudges the assignees without changing status. Run `engine.promote_due()` on a schedule; opening the inbox does the same check.

An edge may name an effect the app registered, such as `post_journal`. The effect can refuse the edge, and the task stays open. The same edge may start another published workflow.

A sign outcome stores the signature, the signer's name, the statement of intent, and a hash of the answers and file hashes. Later edits to the subject record do not rewrite that snapshot.
