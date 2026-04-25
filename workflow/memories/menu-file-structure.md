# Menu File Structure — `menu/*.md`

Menu definitions live in `.a-local-workflow/workflow/menu/`.
Each file covers one menu level and follows this layout:

```markdown
# <Menu Name>

<One-sentence description of what this menu does.>

---

## <Menu Name>

\```
- question: "<question text>"
- header: "<≤12 chars>"
- options:
  1. label "<Label>"  — description "<description>"
  2. label "Back"     — description "Return to the previous menu"
\```

### Routing

1. **<Label>** — <what the agent does when this option is selected, including any prompts,
   session writes, and which agent file to load next>.

2. **Back** — return to `menu/<parent>.md`.
```

---

## Rules

- One `### Routing` block per file, numbered to match the menu options.
- All free-text prompts and session writes belong in the Routing section, not in agent files.
- Agent files start at the first action step — no startup menus.
- When a routing option has multiple sequential sub-actions, list them as `a.` `b.` `c.` — not `-` bullets. Use `-` only for unordered/parallel items (e.g. a list of notes or independent choices).
- Apply the same `a.` `b.` `c.` convention inside **agent step files** (`## Step N` sections) — each sequential action within a step is a lettered sub-step.
- **File references** — always use full workspace-root-relative paths with the `load` verb: `load '.a-local-workflow/workflow/menu/task-lifecycle/index.md'`. Never use relative markdown links (`[file.md](file.md)`) or partial paths (`menu/index.md`). This ensures references work regardless of where the agent reads the file from.
- **Menu definitions** | All `AskUserQuestion` specs live in `workflow-menu.md` — never inline them in agent files.
- **New menus** | Add the menu block to `workflow-menu.md` first, then reference it from the agent file.
- **Do not inline menu blocks in agent files.** Reference the named section in `menu/index.md` instead.
- **Header ≤ 12 characters** — displayed as a chip label above the question.
- **Menu block naming:** use `## Menu` (or `### Menu`) when a file contains only one menu block; use `## <Meaningful Name> Menu` when a file contains two or more menu blocks.
- Every menu that is not the top-level start menu **must** include a `"Back"` option.

---

## Agent Startup Menu Template

In the agent `.md` file, replace the `AskUserQuestion` block with a reference to `workflow-menu.md`:

```
## Startup Menu

**When this agent starts, use the `AskUserQuestion` tool before doing anything else.**

Read the **<Menu Name>** menu from `.a-local-workflow/workflow/workflow-menu.md` and present it
using the `AskUserQuestion` tool.

Branch accordingly:

- **Option A** → ...
- **Option B** → ...
- **Back**     → load `.a-local-workflow/workflow/agents/orchestrator.md` and return
  control to the **Orchestrator Agent**.
```

---

## Entry Point

- **Entry point** | Users trigger the workflow via `/workflow-menu` (Claude slash command in `.claude/commands/`)
- **Slash command** | `.claude/commands/` is excluded from git via `.git/info/exclude` — local-only, not committed

