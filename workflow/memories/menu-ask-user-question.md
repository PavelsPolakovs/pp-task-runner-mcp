# Menu — AskUserQuestion Tool

Use the `AskUserQuestion` tool — **do not** run `menu.js` via Bash. The Bash tool never
allocates a TTY, so `menu.js` always falls back to plain text. `AskUserQuestion` renders
natively in Claude Code with keyboard navigation.

`menu.js` has been **deleted**. All menus use `AskUserQuestion` natively in Claude Code.

---

## Rules

| Rule | Detail |
|---|---|
| Options | 2–4 per menu (a 5th "Other" is added automatically by the tool) |
| Header | Max 12 characters — shown as a label chip above the question |
| `multiSelect` | Always `false` for navigation menus |
| Back option | Every sub-agent menu must include a **Back** option that returns to the Orchestrator |
| Loops | After completing an action, show the menu again so the user can pick another option or go back |

---

## Minimal Two-Option Menu Example

```
Use the `AskUserQuestion` tool:

- **question**: `"What would you like to do?"`
- **header**: `"My Agent"`
- **options**:
  1. label `"Do the thing"` — description `"Runs the main workflow"`
  2. label `"Back"`         — description `"Return to the Orchestrator menu"`
```

