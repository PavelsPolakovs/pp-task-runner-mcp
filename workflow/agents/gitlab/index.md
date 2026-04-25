# GitLab Orchestrator

Coordinates all GitLab-related operations by routing to the appropriate specialist sub-agent based on the current action or user selection.

---

## Sub-agents

| File | Responsibility |
|------|---------------|
| [authentication.md](./authentication.md) | How to authenticate against the GitLab API (token setup, base URLs, tooling rules) |
| [create-issue.md](./create-issue.md) | Create a GitLab issue from a session plan, with duplicate detection and session cleanup |
| [create-branch.md](./create-branch.md) | Create a GitLab branch from the session task, check it out locally, and prompt for next steps |
| [commit-and-push.md](./commit-and-push.md) | Stage all local changes, create a conventional commit, and push to the remote feature branch |
| [merge-branch.md](./merge-branch.md) | Open a merge request from the session branch and merge it into `main` |
| [close-issue.md](./close-issue.md) | Close the GitLab issue linked to the session task and transition it to `workflow::resolved` |

---

## Startup

**On every load, before showing any menu, read the `action` key from the session:**

```bash
node .a-local-workflow/workflow/scripts/session/session.js get action
```

- If `action` is `"create-issue"` → load [create-issue.md](./create-issue.md) and follow its steps.
- If `action` is `"create-branch"` → load [create-branch.md](./create-branch.md) and follow its steps.
- If `action` is `"commit-and-push"` → load [commit-and-push.md](./commit-and-push.md) and follow its steps.
- If `action` is `"merge-branch"` → load [merge-branch.md](./merge-branch.md) and follow its steps.
- If `action` is `"close-issue"` → load [close-issue.md](./close-issue.md) and follow its steps.
- If `action` is empty or absent → continue to the **Startup Menu** below.

---

## Startup Menu

**When no `action` is set, use the `AskUserQuestion` tool before doing anything else.**

```
- question: "What would you like to do?"
- header: "GitLab"
- options:
  1. label "Create issue"       — description "Create a new GitLab issue from the plan in the session"
  2. label "Create branch"      — description "Create a new feature branch linked to a task"
  3. label "Commit and push"    — description "Stage changes, commit with a conventional message, and push to remote"
  4. label "Merge branch"       — description "Open a merge request and merge the branch into main"
  5. label "Close issue"        — description "Close the task linked to the session and mark it as resolved"
  6. label "Back"               — description "Return to the Orchestrator menu"
```

### Routing

1. **Create issue**
   a. Set the session action to `create-issue`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "create-issue"
      ```
   b. Load `.a-local-workflow/workflow/agents/gitlab/create-issue.md` and follow its steps.

2. **Create branch**
   a. Set the session action to `create-branch`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "create-branch"
      ```
   b. Load `.a-local-workflow/workflow/agents/gitlab/create-branch.md` and follow its steps.

3. **Commit and push**
   a. Set the session action to `commit-and-push`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "commit-and-push"
      ```
   b. Load `.a-local-workflow/workflow/agents/gitlab/commit-and-push.md` and follow its steps.

4. **Merge branch**
   a. Set the session action to `merge-branch`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "merge-branch"
      ```
   b. Load `.a-local-workflow/workflow/agents/gitlab/merge-branch.md` and follow its steps.

5. **Close issue**
   a. Set the session action to `close-issue`:
      ```bash
      node .a-local-workflow/workflow/scripts/session/session.js set action "close-issue"
      ```
   b. Load `.a-local-workflow/workflow/agents/gitlab/close-issue.md` and follow its steps.

6. **Back**
   a. Load `.a-local-workflow/workflow/menu/task-lifecycle/index.md` and return control to the **Task Lifecycle Orchestrator**.
