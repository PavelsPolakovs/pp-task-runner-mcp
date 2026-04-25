# Close Issue

Closes the GitLab issue linked to the current session task, transitions its workflow label to `workflow::resolved`, and posts a closing comment.
Uses the **trev-gitlab-workflow** skill for all GitLab API operations. This file contains only UCS-specific inputs and overrides.

---

## UCS Overrides (always apply, take precedence over the skill)

| Concern | UCS rule                                                                                                 |
|---------|----------------------------------------------------------------------------------------------------------|
| **Authentication** | Follow [authentication.md](./authentication.md) — use `curl` with `PRIVATE-TOKEN`. **Never use `glab`.** |
| **Project** | `oaf%2Fucs` (URL-encoded). Do not auto-detect from git remote.                                           |
| **Resolved label** | Transition to `workflow::resolved` — remove the current `workflow::*` label atomically in the same PUT.  |
| **Agent signature** | Closing comment must end with: `Closed by AI coding agent (Claude via <PAT owner>)`                      |

---

## Step 1 — Read the session

a. Read the full session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js get
   ```
b. Extract:
   - `task` — object with `iid`, `title`, `link`
   - `mr` — object with `url`, `iid` (if present)

c. If `task` is absent or has no `iid`:
   - Print: _"No task found in the current session. Please create a task first."_
   - Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.

---

## Step 2 — Close the issue and transition workflow label

a. Compose the message:
   ```bash
   MSG="Closing issue \`#$TASK_IID\` and transitioning to \`workflow::resolved\`…"
   ```

b. Print the message:
   > _"`$MSG`"_

c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

d. Use the **trev-gitlab-workflow** skill's atomic label transition pattern. Authenticate via [authentication.md](./authentication.md), then close the issue and set `workflow::resolved` in one PUT:
   ```bash
   curl -s -X PUT "$GITLAB_API/projects/$PROJECT/issues/$TASK_IID" \
     -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"state_event": "close", "add_labels": "workflow::resolved", "remove_labels": "workflow::in-progress"}' | \
     python3 -c "import json,sys; d=json.load(sys.stdin); print('State:', d.get('state'), '| Labels:', d.get('labels'))"
   ```

   > **Note:** `remove_labels` should match whatever `workflow::*` label is currently on the issue. If unsure, read the issue first (`GET .../issues/$TASK_IID`) and extract the active `workflow::*` label before issuing the PUT.

e. Compose the message:
   ```bash
   MSG="Issue \`#$TASK_IID\` closed and transitioned to \`workflow::resolved\`."
   ```

f. Print the message:
   > _"`$MSG`"_

g. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

---

## Step 3 — Post a closing comment

a. Compose the message:
   ```bash
   MSG="Posting closing comment on issue \`#$TASK_IID\`…"
   ```

b. Print the message:
   > _"`$MSG`"_

c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

d. Use the **trev-gitlab-workflow** skill's **AI Agent Signing** rules. Post a closing comment with the UCS signature:
   ```bash
   python3 -c "
   import json, sys
   print(json.dumps({'body': sys.argv[1]}))
   " "## Resolved

   **Branch:** $BRANCH
   **MR:** $MR_URL

   Issue closed after successful merge into \`main\`.

   ---
   Closed by AI coding agent (Claude via <PAT owner>)" \
     > /tmp/close-issue-comment.json

   curl -s -X POST "$GITLAB_API/projects/$PROJECT/issues/$TASK_IID/notes" \
     -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
     -H "Content-Type: application/json" \
     -d @/tmp/close-issue-comment.json | \
     python3 -c "import json,sys; d=json.load(sys.stdin); print('Comment ID:', d.get('id'))"
   ```

e. Compose the message:
   ```bash
   MSG="Closing comment posted on issue \`#$TASK_IID\`."
   ```

f. Print the message:
   > _"`$MSG`"_

g. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

---

## Step 4 — Clean up the session and return control

a. Clear the entire session — the task lifecycle is complete:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js delete
   ```

b. Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.
