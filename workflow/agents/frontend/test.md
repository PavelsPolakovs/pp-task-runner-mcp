# Frontend Test Agent

## Role

Runs Jest unit/component tests across **all `www/` projects**.
Fixes auto-fixable issues (e.g. snapshot updates), hands off failing tests to the **Frontend Developer** agent, and loops until every test suite passes. On full success, hands control to the **Task Lifecycle Orchestrator**.

## Stack

- React 19, Vite 6, TypeScript strict
- Jest (test runner)
- React Testing Library (component tests)
- Nx monorepo (run-many target: test)

## Responsibilities

- Run Jest test suites across all `www/` projects
- Auto-update snapshots when only snapshot mismatches are detected
- Hand off other failures to the **Frontend Developer** agent with a structured report
- Loop until all suites pass, then hand control to the **Task Lifecycle Orchestrator**

## Brand Isolation Rules

- Tests must run across **all three brands** — `brand-a`, `brand-b`, `brand-c` — not just the affected one
- Changes to `www/libs/` must not bleed theme tokens between brands
- Runtime brand resolution: domain → env var → query param (see `www/libs/core/src/brand-resolver.ts`)

---

## Startup

1. Discover all `www/` projects dynamically:
   a. Run:
      ```bash
      npx nx show projects --json 2>/dev/null \
        | node -e "
            const data = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
            const list = data.filter(name => {
              try {
                const pj = require(\`./\${name}/project.json\`);
                return (pj.root || '').startsWith('www/');
              } catch { return false; }
            });
            console.log(list.join(','));
          "
      ```
   b. Store the comma-separated result as `WWW_PROJECTS` for use in all `--projects` flags below.
   c. If the command fails or returns empty, fall back to:
      `brand-a,brand-b,brand-c,ui,core,brand-a-theme,brand-b-theme,brand-c-theme`

---

## Check Loop

**Repeat the entire loop (1 → 2) until all steps pass without errors.**
Every time control returns from the **Frontend Developer** agent after a fix, restart from step 1.

**Before starting the loop:**

a. Compose the message:
   ```bash
   MSG="Tests started at \`$(date '+%Y-%m-%d %H:%M:%S')\`."
   ```
b. Print the message:
   > _"`$MSG`"_
c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

1. **Run Tests**
   a. Run:
      ```bash
      npx nx run-many -t test --projects=$WWW_PROJECTS 2>&1
      ```
   b. If all tests pass → continue to step 2.
   c. If any tests fail → inspect the output:
      - **Snapshot mismatches only** → auto-update snapshots and re-run:
        ```bash
        npx nx run-many -t test --projects=$WWW_PROJECTS -- --updateSnapshot 2>&1
        ```
        - If re-run passes → continue to step 2.
        - If re-run still fails → **hand off to Frontend Developer** (see [Hand-off Format](#hand-off-format)) and **restart from step 1** when control returns.
      - **Any other failures** → **hand off to Frontend Developer** (see [Hand-off Format](#hand-off-format)) and **restart from step 1** when control returns.

2. **Confirm No Tests Were Skipped Unintentionally**
   a. Check the test output for lines matching `skipped` or `todo`.
   b. Report them in the summary — informational only, do **not** fail the loop for intentionally skipped tests.

**After the loop completes (all tests passed):**

a. Compose the message:
   ```bash
   MSG="Tests finished at \`$(date '+%Y-%m-%d %H:%M:%S')\` — status: \`passed\`."
   ```
b. Print the message:
   > _"`$MSG`"_
c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

## Hand-off Format

When handing off to the **Frontend Developer** agent, always include a structured error report:

```
❌ Test run failed — handing off to Frontend Developer for fixes.

Step:    <Tests>
Files:
  - <file path>:<line> — <test suite / test name>
    Details: <human-readable explanation of what failed and why>
  - <file path>:<line> — ...

Action required:
  Fix the failing tests above. Do NOT delete tests or mark them as `.skip`
  to silence failures. When done, reload test.md to restart the full check
  loop from Step 1.
```

Load `.a-local-workflow/workflow/agents/frontend/developer.md` and transfer control with the report above.

---

## On Full Success

When all test suites pass, print the summary:

```
✓ Tests — all www/ project test suites passed
```

Include a note of any intentionally skipped/todo tests found in Step 2.

## Clean up and return control

a. Unset the `action` key from the session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js unset action
   ```

b. Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.
