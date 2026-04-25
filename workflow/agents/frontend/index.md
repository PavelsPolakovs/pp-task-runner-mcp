# Frontend Orchestrator

Coordinates all frontend-related development tasks by routing to the appropriate specialist sub-agent based on the current action or user selection.

---

## Sub-agents

| File | Responsibility |
|------|---------------|
| [developer.md](./developer.md) | Implement UI features and fixes across the `www/` multi-brand frontend |
| [quality.md](./quality.md) | Run Prettier, ESLint, Typecheck, and Build across all `www/` projects; loop until all pass |
| [reviewer.md](./reviewer.md) | Review frontend code changes for correctness, brand isolation, accessibility, and quality before committing |
| [test.md](./test.md) | Run Jest tests across all `www/` projects; loop until all suites pass |

---

## Startup

**On every load, before showing any menu, read the `action` key from the session:**

```bash
node .a-local-workflow/workflow/scripts/session/session.js get action
```

- If `action` is `"develop"` → load [developer.md](./developer.md) and follow its steps.
- If `action` is `"quality-check"` → load [quality.md](./quality.md) and follow its steps.
- If `action` is `"review"` → load [reviewer.md](./reviewer.md) and follow its steps.
- If `action` is `"test"` → load [test.md](./test.md) and follow its steps.
- If `action` is empty or absent → continue to the **Startup Menu** below.

---

## Startup Menu

**When no `action` is set, use the `AskUserQuestion` tool before doing anything else.**

```
- question: "What would you like to do?"
- header: "Frontend"
- options:
  1. label "Develop feature"   — description "Implement UI features and fixes across the www/ multi-brand frontend"  — action "develop"
  2. label "Quality checks"    — description "Run Prettier, ESLint, Typecheck, and Build across all www/ projects"   — action "quality-check"
  3. label "Review code"       — description "Review frontend changes for correctness, brand isolation, and quality"  — action "review"
  4. label "Run tests"         — description "Run Jest unit/component tests across all www/ projects"                — action "test"
  5. label "Back"              — description "Return to the Task Lifecycle menu"
```

### Routing

1. **Develop feature**
   a. Set the session action to `develop`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "develop"
      ```
   b. Load `.a-local-workflow/workflow/agents/frontend/developer.md` and follow its steps.

2. **Quality checks**
   a. Set the session action to `quality-check`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "quality-check"
      ```
   b. Load `.a-local-workflow/workflow/agents/frontend/quality.md` and follow its steps.

3. **Review code**
   a. Set the session action to `review`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "review"
      ```
   b. Load `.a-local-workflow/workflow/agents/frontend/reviewer.md` and follow its steps.

4. **Run tests**
   a. Set the session action to `test`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "test"
      ```
   b. Load `.a-local-workflow/workflow/agents/frontend/test.md` and follow its steps.

5. **Back**
   a. Load `.a-local-workflow/workflow/menu/task-lifecycle/index.md` and return control to the **Task Lifecycle Orchestrator**.

