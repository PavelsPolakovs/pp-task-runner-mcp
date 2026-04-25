# Named Handoff Blocks

When an agent or menu file hands off control to another agent more than once, define a **named handoff block** at the top of the relevant section, then reference it by name in each step.

---

## Definition

Placed once, before the numbered steps:

```markdown
> **[Handoff to <Agent Name>]**
> Load `<path/to/agent.md>` and transfer control to the **<Agent Name>**.
```

## Reference

Inside a step:

```markdown
b. → **[Handoff to <Agent Name>]**
```

---

## Rules

- Define the block immediately inside the section it belongs to (e.g. `## Workflow`, `### Routing`) — not at the top of the file.
- Name the block after the target agent: `[Handoff to GitLab Orchestrator]`, `[Handoff to Frontend Index Agent]`, etc.
- Use the `→` arrow when referencing the block from a step.
- If a handoff is used only once, inline it directly (`Load '...' and transfer control to the **...**`) — no need for a named block.

---

## Example

Two steps that both hand off to the same agent:

```markdown
> **[Handoff to GitLab Orchestrator]**
> Load `.a-local-workflow/workflow/agents/gitlab/index.md` and transfer control to the **GitLab Orchestrator**.

1. **Create issue**
   a. Set the session action...
   b. → **[Handoff to GitLab Orchestrator]**

2. **Create branch**
   a. Set the session action...
   b. → **[Handoff to GitLab Orchestrator]**
```

