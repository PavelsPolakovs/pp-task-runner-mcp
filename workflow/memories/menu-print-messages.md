# Print Messages — Agent Status & Confirmation

Use blockquote + italic syntax for all agent status/confirmation messages:

```markdown
> _"Branch `<branch-name>` created successfully."_
```

---

## Rules

- Wrap the entire message in `> _"..."_` (blockquote + italics + quotes).
- Use backticks for inline code values (branch names, file paths, identifiers).
- Use `**bold**` for emphasis on key dynamic values (task titles, etc.).
- Substitute real runtime values — never print the placeholder text literally.
- Print messages belong inside the numbered step where the action occurs (sub-step `b.`, `c.`, etc.), not in a separate section.

## Print-then-Log Pattern

Whenever a step both prints a status message **and** logs it, compose `$MSG` first, then print and log from the variable — so the text is defined exactly once:

```markdown
c. Compose the message:
   ```bash
   MSG="<message text with `runtime values`>."
   ```

d. Print the message:
   > _"`$MSG`"_

e. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```
```

### Rules

- Always define `$MSG` **before** printing or logging — never duplicate the string.
- The `$MSG` variable is ephemeral (shell-local); it is not persisted to the session.
- Print sub-step (`d.`) always comes **after** composition and **before** logging.
- Pass `$MSG` verbatim to the logger — do not re-wrap it; `logger.js` handles formatting.
- **Each action (compose / print / log) MUST be its own lettered sub-step** (`c.` `d.` `e.`). Never nest unlabeled "Print the message:" or "Log the message:" items under a single letter — that form is forbidden.

---

## Examples

```markdown
c. Compose the message:
   ```bash
   MSG="Session started at `$START_TIME`."
   ```

d. Print the message:
   > _"`$MSG`"_

e. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```
```

```markdown
c. Compose the message:
   ```bash
   MSG="Issue \`$PLAN_TITLE\` ($ISSUE_URL) created successfully (\`#$ISSUE_IID\`, \`$ISSUE_TYPE\`, \`workflow::new\`)."
   ```

d. Print the message:
   > _"`$MSG`"_

e. Log the message:
   ```bash
   node .a-local-workflow/workflow/scripts/logger.js log "$MSG"
   ```
```

---


```markdown
> _"Branch `feat/my-feature` created successfully."_
> _"Switched to branch `feat/my-feature`. Task: **Add login page** — Implement the login page UI."_
> _"No task found in the current session. Please create a task first."_
```

