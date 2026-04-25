# Menu System — Entry Point

Single source of truth for all interactive menus used by workflow agents.
Each section defines one named menu block. Agents reference sections by name — never inline menu definitions inside agent files.

> Rules for menu files are maintained in `.a-local-workflow/workflow/memories/menu-file-structure.md`.

---

## Start Menu

### Before displaying this menu — initialize the session

**Execute the following steps in order. Do NOT skip any step. Do NOT simulate output — always run actual terminal commands.**

**Step 1 — Initialize the session (only if not already started):**

a. Clear stale data:
   - Clear session data:
     ```bash
     node .a-local-workflow/workflow/scripts/session/session.js delete
     ```
   - Clear logger data:
     ```bash
     node .a-local-workflow/workflow/scripts/logger.js clear
     ```

b. Run this command and capture the output:
```bash
node .a-local-workflow/workflow/scripts/session/session.js get startedAt
```
If the output is empty, run:
```bash
node .a-local-workflow/workflow/scripts/session/session.js init
```

c. Compose the message:
   ```bash
   MSG="Session started at `<startedAt>`."
   ```

d. Print the message:
   > _"`$MSG`"_

e. Log the message:
```bash
node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
```

---

### Menu

```
- question: "What would you like to do?"
- header: "Start Menu"
- options:
  1. label "Task Lifecycle"  — description "Run the full task flow: from plan file to closed task"
  2. label "Show logs"       — description "Display all recorded workflow log entries"
  3. label "Exit"            — description "End the session and delete session data"
```

### Routing

1. **Task Lifecycle** — load `.a-local-workflow/workflow/menu/task-lifecycle.md` and transfer control to the **Task Lifecycle Orchestrator**.
2. **Show logs** — run the following command and print its output to the conversation exactly as-is:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js list
   ```
   Then re-display this menu.
3. **Exit** — end the session and delete session data.
