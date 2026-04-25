# Claude Commands — Local-Only Setup

## What

`.claude/commands/` contains personal Claude slash commands (e.g. `/workflow-menu`).
This directory is **not committed** — it is excluded from git locally.

## Why not committed

Other team members may commit their own files to `.claude/commands/`. Ignoring the
whole directory via a shared `.gitignore` would block that. Instead, each developer
manages their own local commands privately.

## How it is excluded

The directory is listed in `.git/info/exclude` (local-only, never pushed):

```
.claude/commands/
```

This file lives at `.git/info/exclude` in the repo root. It works identically to
`.gitignore` but is never committed or shared.

## How to set up on a new machine / fresh clone

Run once after cloning:

```bash
echo '.claude/commands/' >> .git/info/exclude
mkdir -p .claude/commands
```

Then create whichever slash command files you need personally, e.g.:

```bash
cp .a-local-workflow/workflow/workflow-menu.md .claude/commands/workflow-menu.md
```

Or write your own content — the file just needs to contain instructions for Claude.

## Verification

After setup, `.claude/commands/` must NOT appear in `git status`:

```bash
git status --short | grep '.claude/commands'
# expected: no output
```

