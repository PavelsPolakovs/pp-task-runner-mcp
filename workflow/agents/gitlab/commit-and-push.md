# Commit and Push

Stages all local changes, creates a conventional commit, and pushes to the remote feature branch.
Uses the **trev-gitlab-workflow** skill for commit message format and push operations. This file contains only UCS-specific inputs and overrides.

---

## UCS Overrides (always apply, take precedence over the skill)

| Concern | UCS rule |
|---------|----------|
| **Co-author trailer** | Always use `Co-Authored-By: Claude <agent> <noreply@anthropic.com>` (not `Claude Code`) |
| **Refs line** | If the session contains a `task.link`, append `Refs: <task-link>` between the subject and the trailer |
| **Commit** | Automatically derive commit message (`type(scope): description`) from the branch prefix and changed files. Do **not** prompt for confirmation — stage, commit, and push immediately. |

---

## Step 1 — Read the session

a. Read the full session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js get
   ```
b. Extract:
   - `branch` — the current feature branch name
   - `task` — object with `title` and `link`

c. If `branch` is absent or empty:
   - Print: _"No branch found in the current session. Please create a branch first."_
   - Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.

d. Confirm the local working copy is on that branch:
   ```bash
   git rev-parse --abbrev-ref HEAD
   ```
   If it does not match, check out the correct branch:
   ```bash
   git checkout <branch-name>
   ```

---

## Step 2 — Show the diff

a. Print a summary of changed files so the user can review before committing:
   ```bash
   git status --short
   ```

---

## Step 3 — Commit and push

a. Compose the message:
   ```bash
   MSG="Committing and pushing branch \`$BRANCH\` for task $TASK_LINK."
   ```

b. Print the message:
   > _"`$MSG`"_

c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

d. Use the **trev-gitlab-workflow** skill for commit message format, staging, committing, and pushing. Apply all UCS overrides from the table above:
   - Derive commit message (`type(scope): description`) from the branch prefix and changed files
   - Append `Refs: <task-link>` from the session task (UCS override)
   - Append `Co-Authored-By: Claude <agent> <noreply@anthropic.com>` trailer (UCS override)
   - Stage all changes, commit, and push to `origin/<branch-name>` immediately (no confirmation prompt)

e. Compose the message:
   ```bash
   MSG="Branch \`$BRANCH\` pushed to origin successfully."
   ```

f. Print the message:
   > _"`$MSG`"_

g. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

---

## Step 4 — Clean up and return control

a. Unset the `action` key from the session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js unset action
   ```

b. Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.
