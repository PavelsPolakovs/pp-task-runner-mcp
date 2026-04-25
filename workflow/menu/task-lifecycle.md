# Task Lifecycle Orchestrator Menu

The Task Lifecycle Orchestrator is the second level of the menu system, reached after the user selects **Task Lifecycle** from the Start Menu.
It routes the user to the correct specialist or utility for the current phase of task work.

---

## Menu

```
- question: "What would you like to do?"
- header: "Task Lifecycle"
- options:
  1. label "Create issue"     — description "Create a new GitLab issue from a plan file"
  2. label "Create branch"    — description "Create a GitLab branch from the session task and check it out locally"
  3. label "Commit and push"  — description "Stage changes, commit with a conventional message, and push to the remote branch"
  4. label "Merge branch"     — description "Open a merge request and merge the branch into main"
  5. label "Close issue"      — description "Close the task linked to the session and mark it as resolved"
  6. label "Complete task"    — description "Develop and complete the current task using the Frontend agent"
  7. label "Quality checks"   — description "Run Prettier, ESLint, Typecheck, and Build across all www/ projects"
  8. label "Run tests"        — description "Run Jest unit/component tests across all www/ projects"
  9. label "Back"             — description "Return to the Start Menu"
```

### Routing

> **[Handoff to GitLab Orchestrator]**
> Load `.a-local-workflow/workflow/agents/gitlab/index.md` and transfer control to the **GitLab Orchestrator**.

1. **Create issue**
2. a. Print the following message in the chat and wait for the user to reply:
   > _"Please provide the path to the plan file:"_
   b. Treat the user's next message as the plan file path. If the value is empty or blank, re-prompt once with the same message before proceeding.
   c. Once a non-empty path is received, save it to the session:
   ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set planFile "<received-path>"
   ```
   d. Set the session action to `create-issue`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "create-issue"
      ```
   f. → **[Handoff to GitLab Orchestrator]**

2. **Create branch**
   a. Set the session action to `create-branch`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "create-branch"
      ```
   b. → **[Handoff to GitLab Orchestrator]**

3. **Commit and push**
   a. Set the session action to `commit-and-push`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "commit-and-push"
      ```
   b. → **[Handoff to GitLab Orchestrator]**

4. **Merge branch**
   a. Set the session action to `merge-branch`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "merge-branch"
      ```
   b. → **[Handoff to GitLab Orchestrator]**

5. **Close issue**
   a. Set the session action to `close-issue`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "close-issue"
      ```
   b. → **[Handoff to GitLab Orchestrator]**

6. **Complete task**
   a. Set the session action to `develop`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "develop"
      ```
   b. Load `.a-local-workflow/workflow/agents/frontend/index.md` and transfer control to the **Frontend Agent**.

7. **Quality checks**
   a. Set the session action to `quality-check`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "quality-check"
      ```
   b. Load `.a-local-workflow/workflow/agents/frontend/index.md` and transfer control to the **Frontend Agent**.

8. **Run tests**
   a. Set the session action to `test`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "test"
      ```
   b. Load `.a-local-workflow/workflow/agents/frontend/index.md` and transfer control to the **Frontend Agent**.

9. **Back**
   a. Return to the Start Menu — load `.a-local-workflow/workflow/menu/index.md`.
