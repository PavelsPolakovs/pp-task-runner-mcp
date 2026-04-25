# Create Branch

Creates a GitLab branch from the current session task, checks it out locally, and prompts for next steps.
Uses the **trev-gitlab-workflow** skill for all branching operations. This file contains only UCS-specific inputs and overrides.

---

## UCS Overrides (always apply, take precedence over the skill)

| Concern | UCS rule |
|---------|----------|
| **Authentication** | Follow [authentication.md](./authentication.md) — use `curl` with `PRIVATE-TOKEN`. **Never use `glab`.** |
| **Project** | `oaf%2Fucs` (URL-encoded). Do not auto-detect from git remote. |
| **Branch name** | Automatically derive the branch name from the session task (`iid`, `title`, `type::*` label) using the skill's naming convention (`feat/cli-<IID>-<slug>`). Do **not** prompt for confirmation — proceed immediately. |

---

## Step 1 — Read the task from the session

a. Read the current session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js get
   ```
b. If the session contains a `task` object (with `link`, `iid`, `title`) — parse and use those details directly.
c. If `task` is not present:
   - Print: _"No task found in the current session. Please create a task first."_
   - Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.

---

## Step 2 — Create the branch

a. Compose the message:
   ```bash
   MSG="Creating branch based on task $TASK_LINK."
   ```

b. Print the message:
   > _"`$MSG`"_

c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

d. Use the **trev-gitlab-workflow** skill for all operations, applying all UCS overrides from the table above:
   - Sync local `main` before branching
   - Derive branch name from the session task (`iid`, `title`, `type::*` label) using the skill's naming convention (`feat/cli-<IID>-<slug>`)
   - Create the branch via GitLab API and check it out locally (no confirmation prompt)
   - Immediately push the branch to remote so it exists on GitLab:
     ```bash
     git push -u origin <branch-name>
     ```

---

## Step 3 — Confirm branch created

a. Compose the push log message:
   ```bash
   MSG="Branch \`<branch-name>\` pushed to remote."
   ```

b. Print the message:
   > _"`$MSG`"_

c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

d. Compose the message:
   ```bash
   MSG="Branch \`<branch-name>\` created and checked out."
   ```

e. Print the message:
   > _"`$MSG`"_

f. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

---

## Step 4 — Save the branch to the session

a. Save the branch name to the session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js set branch "<branch-name>"
   ```

---

## Step 5 — Clean up and return control

a. Unset the `action` key from the session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js unset action
   ```

b. Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.
