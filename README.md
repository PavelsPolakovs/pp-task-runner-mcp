# pp-task-runner MCP

A minimal MCP server that opens an interactive browser-based skill selection menu inside Claude Code. Skills are predefined actions — the browser card lets you pick one with a single click, and Claude Code receives the selection immediately.

## Prerequisites

- Python 3.10+
- `pip` available in your environment

Install Python dependencies once:

```bash
pip install --user -r requirements.txt
```

## Installation in Claude Code

Add the server with `claude mcp add`. Two options depending on whether you have a local clone:

**Local clone (recommended):**

```bash
claude mcp add --transport stdio pp-task-runner -- \
  python3 /path/to/pp-task-runner-mcp/server.py
```

**On-the-fly from GitLab (no clone needed):**

```bash
claude mcp add --transport stdio pp-task-runner -- sh -c \
  'git clone https://gitlab.com/PavelsPolakovs/pp-task-runner-mcp.git /tmp/pp-task-runner-mcp \
   && pip install -q -r /tmp/pp-task-runner-mcp/requirements.txt \
   && python3 /tmp/pp-task-runner-mcp/server.py'
```

Verify the server connected:

```bash
claude mcp list
```

You should see `pp-task-runner` listed with status `connected`.

## Starting the Menu

Once the MCP server is installed, type `/start-pp-task-runner` in Claude Code.

Claude Code calls the `open_menu` tool, which starts a local HTTP server on a random free port and opens your default browser automatically. Select a task in the browser — Claude Code receives the event and responds.

## Browser UI

The browser opens a card UI at `http://127.0.0.1:<random-port>` with:

- A button for every skill defined in `src/menu_mcp/constants.py`
- An **Exit** button to close the menu cleanly
- A status line that confirms the selection was sent to Claude Code

The local HTTP server shuts down automatically after any of the following:

| Event | Browser shows | Claude Code receives |
|---|---|---|
| Task button clicked | "✓ Done" | `{"action": "greet", "name": "…", "message": "…"}` |
| Exit button clicked | "Closing…" | `{"action": "exit"}` |
| Tab / window closed | — | `{"action": "close"}` |
| 5-minute timeout | — | `{"action": "timeout"}` |

Claude Code loops on `open_menu` calls until it receives `exit`, `close`, or `timeout`.

## Configuration

### Adding tasks

Edit `src/menu_mcp/constants.py` (or provide `task_config.json` in the repo root):

```python
TASKS = {
    "My Task": "Description shown under the button",
    "Another Task": "Does something else",
}
```

Each key becomes a button label; the value is shown as a subtitle and sent to Claude Code as the message when selected.

### Environment variables

| Variable | Purpose |
|---|---|
| `MCP_SELECTED_NAME` | Pre-select a task on startup without opening the browser |
| `MCP_SELECTED_URL` | Optional URL stored alongside the pre-selected task |

Pre-selection example (useful in non-interactive or CI environments):

```bash
claude mcp add --transport stdio pp-task-runner -- sh -c \
  'MCP_SELECTED_NAME="My Skill" python3 /path/to/server.py'
```

## Available MCP Tools

| Tool | Description |
|---|---|
| `open_menu` | Open the browser menu or wait for the next user action |
| `select_skill` | Activate a task by name without opening the browser |
| `get_active_skill` | Return the currently active task name and description |
| `list_skills` | Return all available tasks as a JSON array |
| `update` | Pull latest changes from the remote repo (`git pull`) |

After calling `update`, reconnect the server in Claude Code: `/mcp` → **Reconnect** `pp-task-runner`.

## Testing Outside Claude Code

Three modes are available, all work without Claude Code.

### 1. Simulate — full Claude Code flow (`make simulate`)

`simulate.py` imports the server code directly (no subprocess) and calls `open_menu` in a loop — handling each event exactly as the `/start-pp-task-runner` skill instructs Claude Code to do. Running in-process means `webbrowser.open()` fires in the same Python process, so the browser opens reliably. The menu URL is always printed to the terminal as a fallback.

```bash
make simulate
# or
python3 simulate.py
```

What happens:
1. FastMCP app and tools are initialised in-process
2. `open_menu` is called → URL printed to terminal, browser opens at `http://127.0.0.1:<port>`
3. Click a skill / Exit / close the tab → event printed to the terminal, exits
4. Run `make simulate` again to reopen the menu

If the browser doesn't open automatically, copy the URL from the terminal and paste it into any browser.

### 2. Inspector — interactive tool calls (`make dev`)

`mcp dev` launches the official MCP Inspector: a browser GUI where you can call any MCP tool by hand, exactly as Claude Code does internally.

```bash
# Install dev dependencies (adds pytest)
pip install -r requirements-dev.txt

# Open the Inspector
make dev
# or
mcp dev dev_server.py:mcp
```

The Inspector opens at `http://localhost:5173`. Select a tool from the sidebar, fill in arguments, and click **Run** — the tool executes and you see the raw JSON response.

### Automated — pytest

The test suite covers tool logic and the full browser-click flow without opening a real browser.

```bash
make test
# or
python3 -m pytest -v
```

### 3. Automated — pytest (`make test`)

**`tests/test_tools.py`** — in-process unit tests (no subprocess, no browser):
- `list_skills` returns the correct schema
- `select_skill` activates a known skill and rejects unknown ones
- `get_active_skill` reflects state after a selection
- `update` parses `git pull` output correctly

**`tests/test_menu_flow.py`** — integration tests for the HTTP server flow:
- `open_menu` starts the local HTTP server and returns a `greet` event when a skill is clicked
- `exit` and `close` events work correctly
- The HTML page is served with the correct skill buttons
- The HTTP server shuts down after the user interacts

`webbrowser.open` is mocked in all flow tests so no real browser opens; HTTP POST calls go directly to the ephemeral server at `127.0.0.1:<random-port>`.

## Project Structure

```
pp-task-runner-mcp/
├── server.py              Entry point — sets PYTHONPATH and delegates to src.main
├── simulate.py            Claude Code simulator — spawns server.py and drives it via MCP
├── dev_server.py          Module-level FastMCP instance for `mcp dev`
├── menu_server.py         Standalone variant (Monitor-based, no MCP required)
├── Makefile               up / dev / test targets
├── requirements.txt       Runtime Python dependencies
├── requirements-dev.txt   Adds pytest for testing
├── pytest.ini             Configures testpaths and pythonpath
├── tests/
│   ├── conftest.py        Fixtures: fresh mcp_app per test, _menu state reset
│   ├── test_tools.py      Unit tests for non-browser tools
│   └── test_menu_flow.py  Integration tests for the open_menu HTTP flow
└── src/
    ├── main.py            FastMCP server entry point
    └── menu_mcp/
        ├── constants.py   SKILLS registry and timeout setting
        ├── state.py       Shared HTTP server state
        ├── tools.py       MCP tool registrations
        └── web.py         HTTP handler and browser UI HTML
```

## Local Development

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install dev dependencies (includes pytest)
pip install -r requirements-dev.txt

# Run the menu locally (simulate the menu flow)
make up
# or
python3 server.py --transport stdio
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Browser doesn't open | Check that a default browser is configured (`xdg-open` on Linux, `open` on macOS) |
| `pp-task-runner` not listed in `claude mcp list` | Re-run `claude mcp add …` and check the path to `server.py` |
| `ModuleNotFoundError` on startup | Run `pip install -r requirements.txt` |
| Menu times out immediately | The server couldn't bind a port — check for firewall rules blocking `127.0.0.1` |