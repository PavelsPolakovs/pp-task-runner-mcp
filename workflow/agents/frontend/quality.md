# Frontend Quality Agent

## Role

Runs Prettier, ESLint, TypeScript typecheck, and build verification across **all `www/` projects**.
Fixes auto-fixable issues, hands off unfixable errors to the **Frontend Developer** agent, and loops until every check passes. On full success, hands control to the **Task Lifecycle Orchestrator**.

## Stack

- React 19, Vite 6, TypeScript strict
- Prettier (formatting)
- ESLint (linting)
- Nx monorepo (run-many targets: lint, typecheck, build)

## Responsibilities

- Run Prettier, ESLint, TypeScript typecheck, and build across all `www/` projects
- Auto-fix formatting issues (Prettier only) — never suppress lint or type errors
- Hand off unfixable errors to the **Frontend Developer** agent with a structured report
- Loop until all checks pass, then hand control to the **Task Lifecycle Orchestrator**

## Brand Isolation Rules

- Checks must run across **all three brands** — `brand-a`, `brand-b`, `brand-c` — not just the affected one
- Theme token bleed between brands is treated as a type or lint error, not a style preference
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

**Repeat the entire loop (1 → 4) until all steps pass without errors.**
Every time control returns from the **Frontend Developer** agent after a fix, restart from step 1.

**Before starting the loop:**

a. Compose the message:
   ```bash
   MSG="Quality checks started at \`$(date '+%Y-%m-%d %H:%M:%S')\`."
   ```
b. Print the message:
   > _"`$MSG`"_
c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

1. **Prettier**
   a. Check formatting:
      ```bash
      npx prettier --check "www/**/*.{ts,tsx,mjs,json}" --ignore-path .gitignore 2>&1
      ```
   b. If check fails — auto-fix:
      ```bash
      npx prettier --write "www/**/*.{ts,tsx,mjs,json}" --ignore-path .gitignore 2>&1
      ```
   c. Re-check after fix:
      ```bash
      npx prettier --check "www/**/*.{ts,tsx,mjs,json}" --ignore-path .gitignore 2>&1
      ```
   d. If re-check passes → continue to step 2.
      If still fails → **hand off to Frontend Developer** (see [Hand-off Format](#hand-off-format)) and **restart from step 1** when control returns.

2. **ESLint**
   a. Run:
      ```bash
      npx nx run-many -t lint --projects=$WWW_PROJECTS 2>&1
      ```
   b. Errors **must be fixed in code** — no blanket auto-fix. Do **not** suggest `// eslint-disable` unless the rule is a confirmed false positive with no alternative.
   c. If no errors → continue to step 3.
      If errors found → **hand off to Frontend Developer** (see [Hand-off Format](#hand-off-format)) and **restart from step 1** when control returns.

3. **TypeScript Typecheck**
   a. Run:
      ```bash
      npx nx run-many -t typecheck --projects=$WWW_PROJECTS 2>&1
      ```
   b. Do **not** suggest `as any`, `@ts-ignore`, or `@ts-expect-error` unless caused by a known third-party library gap with no alternative.
   c. If no errors → continue to step 4.
      If errors found → **hand off to Frontend Developer** (see [Hand-off Format](#hand-off-format)) and **restart from step 1** when control returns.

4. **Build** — runs **all** `www/` projects, not just affected ones.
   a. Run:
      ```bash
      npx nx run-many -t build --projects=$WWW_PROJECTS 2>&1
      ```
   b. If build succeeds → **all checks passed** → see [On Full Success](#on-full-success).
       If build fails → **hand off to Frontend Developer** (see [Hand-off Format](#hand-off-format)) and **restart from step 1** when control returns.

**After the loop completes (all checks passed):**

a. Compose the message:
   ```bash
   MSG="Quality checks finished at \`$(date '+%Y-%m-%d %H:%M:%S')\` — status: \`passed\`."
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
❌ Quality check failed — handing off to Frontend Developer for fixes.

Step:    <Prettier | ESLint | Typecheck | Build>
Files:
  - <file path>:<line> — <rule name or TS error code>
    Details: <human-readable explanation of what needs to be fixed>
  - <file path>:<line> — ...

Action required:
  Fix the issues above. Do NOT use suppression comments or `any` casts unless
  genuinely unavoidable (see quality.md rules). When done, reload quality.md
  to restart the full check loop from Step 1.
```

Load `.a-local-workflow/workflow/agents/frontend/developer.md` and transfer control with the report above.

---

## On Full Success

When Steps 1, 2, 3, and 4 all pass, print the summary:

```
✓ Prettier  — all www/ files formatted
✓ ESLint    — no errors in www/ projects
✓ Typecheck — no type errors in www/ projects
✓ Build     — all www/ projects built successfully
```

## Clean up and return control

a. Unset the `action` key from the session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js unset action
   ```

b. Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.
