# GitLab Authentication

Provides `GITLAB_TOKEN`, `GITLAB_API`, and `PROJECT` to all GitLab agents.
`GITLAB_TOKEN` is cached in the session so the token is only read from `~/.bashrc` once per session.

---

## How to authenticate

Run the following block **once per agent step** that needs to make API calls:

```bash
# 1. Try to load the token from the session cache
GITLAB_TOKEN=$(node .a-local-workflow/workflow/scripts/session/session.js get gitlabToken)

# 2. If not cached yet, read from ~/.bashrc and persist to the session
if [ -z "$GITLAB_TOKEN" ]; then
  GITLAB_TOKEN=$(grep 'GITLAB_PERSONAL_ACCESS_TOKEN' ~/.bashrc | sed 's/.*"\(.*\)"/\1/')
  node .a-local-workflow/workflow/scripts/session/session.js set gitlabToken "$GITLAB_TOKEN"
fi

# 3. Set the shared constants (always the same, no session storage needed)
GITLAB_API="https://gitlab.dyninno.net/api/v4"
PROJECT="oaf%2Fucs"
```

After this block, `GITLAB_TOKEN`, `GITLAB_API`, and `PROJECT` are available for the rest of the step.

---

## Rules

- Use `GITLAB_TOKEN` as the value for the `PRIVATE-TOKEN` header in every `curl` request.
- **Never use `glab`.** All GitLab operations must be performed with `curl` against `$GITLAB_API`.
- **No confirmation is required** before executing any `curl` request to the GitLab API — run them directly.
- Use `python3` to parse all JSON responses (never `jq`).
