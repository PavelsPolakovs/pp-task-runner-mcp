# Merge Request

Opens a GitLab merge request from the current session branch and merges it into `main`.
Uses the **trev-gitlab-workflow** skill for all MR operations. This file contains only UCS-specific inputs and overrides.

---

## UCS Overrides (always apply, take precedence over the skill)

| Concern | UCS rule |
|---------|----------|
| **Authentication** | Follow [authentication.md](./authentication.md) — use `curl` with `PRIVATE-TOKEN`. **Never use `glab`.** |
| **Project** | `oaf%2Fucs` (URL-encoded). Do not auto-detect from git remote. |
| **Target branch** | Always `main`. |
| **Squash** | Always `true`. |
| **Remove source branch** | Always `true`. |
| **Auto-close issue** | Always include `Closes #<task.iid>` in the MR description if session contains a `task` object. |
| **Agent signature** | Add to MR description footer: `Created by AI coding agent (Claude via <PAT owner>)` |

---

## Step 1 — Read the session

a. Read the full session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js get
   ```
b. Extract:
   - `branch` — the feature branch to merge
   - `task` — object with `iid`, `title`, `link`

c. If `branch` is absent or empty:
   - Print: _"No branch found in the current session. Please create and push a branch first."_
   - Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.

---

## Step 2 — Open the merge request

a. Compose the message:
   ```bash
   MSG="Opening MR for branch \`$BRANCH\` → \`main\` (task $TASK_LINK)."
   ```

b. Print the message:
   > _"`$MSG`"_

c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

d. Use the **trev-gitlab-workflow** skill to create the MR. Apply all UCS overrides from the table above:
   - MR title: derive from session `branch` and `task.title` using the skill's conventional commit title format
   - MR description: use the skill's mandatory MR description template (`## Summary`, `### Changes`, `### How to Test`, `Closes #<iid>`, agent signature)
   - `squash: true`, `remove_source_branch: true` (UCS override)
   - Target branch: `main` (UCS override)
   - Store the response `web_url` as `MR_URL` and `iid` as `MR_IID`

e. Save the MR URL and IID to the session:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js set mr "$(python3 -c "
   import json, sys
   print(json.dumps({'url': sys.argv[1], 'iid': sys.argv[2]}))
   " "$MR_URL" "$MR_IID")"
   ```

f. Compose the message:
   ```bash
   MSG="MR \`!$MR_IID\` opened: $MR_URL."
   ```

g. Print the message:
   > _"`$MSG`"_

h. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

---

## Step 3 — Check pipeline status

a. Compose the message:
   ```bash
   MSG="Pipeline started at \`$(date '+%Y-%m-%d %H:%M:%S')\`. Waiting for it to finish…"
   ```

b. Print the message:
   > _"`$MSG`"_

c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

d. Use the **trev-gitlab-workflow** skill to **poll** the pipeline for the MR branch every **10 seconds** until it reaches a terminal state (`passed`, `success`, `failed`, `canceled`, `skipped`). Do **not** proceed to Step 4 while the pipeline is still `running` or `pending`. **Ignore any polling timeout if the pipeline has already reached a terminal state** — a finished pipeline always takes priority over a timeout error.

e. Compose the message:
   ```bash
   PIPELINE_FINISHED_AT=$(date '+%Y-%m-%d %H:%M:%S')
   MSG="Pipeline finished at \`$PIPELINE_FINISHED_AT\` — status: \`$PIPELINE_STATUS\`."
   ```

f. Print the message:
   > _"`$MSG`"_

g. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

h. Branch on result:
   - If `$PIPELINE_STATUS` is `failed` or `canceled` → print: _"Pipeline failed. Fix the issues and push again before merging."_ → go to Step 5.
   - If `$PIPELINE_STATUS` is `passed`, `success`, `skipped`, or no pipeline → continue to Step 4.

---

## Step 4 — Merge the MR

a. Compose the message:
   ```bash
   MSG="Merging MR \`!$MR_IID\` into \`main\`…"
   ```

b. Print the message:
   > _"`$MSG`"_

c. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

d. Authenticate via [authentication.md](./authentication.md), then merge:
   ```bash
   curl -s -X PUT "$GITLAB_API/projects/$PROJECT/merge_requests/$MR_IID/merge" \
     -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"squash": true, "should_remove_source_branch": true}' | \
     python3 -c "import json,sys; d=json.load(sys.stdin); print('State:', d.get('state', d))"
   ```
   Run post-merge cleanup:
   ```bash
   git checkout main && git pull
   ```

e. Compose the message — use the appropriate variant:
   - If merged:
     ```bash
     MSG="Branch \`$BRANCH\` merged into \`main\` successfully."
     ```
   - If not mergeable:
     ```bash
     MSG="MR \`!$MR_IID\` is not ready to merge automatically. Check $MR_URL and merge manually."
     ```

f. Print the message:
   > _"`$MSG`"_

g. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```

---

## Step 5 — Clean up the session and return control

a. Unset session keys no longer needed:
   ```bash
   node .a-local-workflow/workflow/scripts/session/session.js unset action
   ```

b. Load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.
