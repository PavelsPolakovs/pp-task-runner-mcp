# my-mcp-server

Initial MCP (Model Context Protocol) server structure using FastMCP.

## Setup

This project requires Python 3. The instructions below separate installing
pip (if missing) from project-specific setup (installing dependencies and
creating a `.env` file). If you already have pip available for your Python 3
interpreter you can skip the "Install pip" section and go straight to
"Project setup".

Prerequisites
- Python 3.x installed.
- pip available for that Python interpreter (recommended to use a virtual
  environment).

Install pip (if needed)

This repository includes a Makefile helper that can attempt to install or
bootstrap pip for the selected Python interpreter. It will try Python's
`ensurepip`, fall back to common platform package managers, and finally use
the PyPA bootstrap script as a last resort.

Use the Makefile helper:

```bash
make ensure-pip
```

If you prefer to install pip manually, use your OS package manager or the
standard Python bootstrap methods (for example, `sudo apt install python3-pip`
on Debian/Ubuntu, `brew install python` on macOS, or `python -m ensurepip`),
then continue with the "Project setup" steps below.

Project setup (install dependencies and create config)
```bash
# (recommended) create and activate a virtual environment first:
python3 -m venv .venv
source .venv/bin/activate

# Upgrade packaging tools and install project requirements:
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt

# Copy example environment and edit values as needed:
cp .env.example .env
```

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
copy .env.example .env
```

If you prefer to use the Makefile helper:
```bash
# Attempt to ensure pip is available for the selected Python interpreter
# (this runs the `ensure-pip` target which bootstraps pip or falls back to
# common package managers), or run the installer which invokes it for you:
make ensure-pip

# Install development dependencies (this target calls `ensure-pip` first):
make install-dev
```

The Makefile `ensure-pip` target will attempt to bootstrap pip via Python's
`ensurepip` module and, if that fails, will try common platform package
managers (apt/yum/brew) where appropriate. Use `make ensure-pip` if you want
to only install pip; use `make install-dev` to ensure pip is present and then
install the project's requirements.

Notes:
- Use `python3 -m pip` to ensure pip matches the interpreter you intend to use.
- `cp .env.example .env` is a project configuration step — edit `.env` to add
  secrets or API keys (the example file is checked in, secrets are not).
- Virtual environments are recommended to avoid modifying the system Python.

## Run

```bash
# STDIO transport (Claude Desktop, Cursor, etc.)
python -m src.main --transport stdio

# SSE transport (HTTP-based clients)
python -m src.main --transport sse
```

## Package layout / imports

This project uses the `src` package as the primary import root. The implementation
for the MCP server lives under `src/mcp/...` and the project is intended to be run
with the module form so relative imports resolve correctly. Example:

```bash
# Run the server as a module so imports like `from .mcp...` work:
python -m src.main --transport stdio
```

Note: A top-level `mcp/` shim (that duplicated `src/mcp`) was previously included
for convenience during development. That shim has been removed — the project now
uses package-local imports and the `Makefile` targets have been validated to work
without the shim.

## Examples: start the MCP server for Copilot and Claude Code

Below are concrete examples showing how to start this MCP server so it can be used by local developer tools (VS Code / Copilot) and by Claude (Desktop / Code) clients. Adjust the `cwd` path to the absolute path of this repository on your machine.

### PhpStorm (for Copilot or local development in JetBrains IDEs)

If you use PhpStorm (or other JetBrains IDEs) you can run the MCP server from a Run/Debug configuration or via an External Tool. Below are two options.

Option A — Run/Debug Configuration (recommended when Python support is enabled):

1. Open Run -> Edit Configurations...
2. Click + -> Python configuration.
3. Configure:
   - Name: `Run MCP Server (stdio)`
   - Module name: `src.main` (or Script path: leave empty if using module)
   - Parameters: `--transport stdio`
   - Working directory: `/absolute/path/to/my-mcp-server`
   - Python interpreter: select your project interpreter
4. Apply and Run the configuration. The server output will appear in the Run tool window.

Option B — External Tool (works without Python run configuration):

1. Open Settings/Preferences -> Tools -> External Tools.
2. Click + to add a new external tool with values:
   - Name: `Run MCP Server (stdio)`
   - Program: `python`
   - Arguments: `-m src.main --transport stdio`
   - Working directory: `$ProjectFileDir$`
3. Save. Run it from Tools -> External Tools -> Run MCP Server (stdio).

Alternatively you can run the same command in PhpStorm's built-in terminal:

```bash
python -m src.main --transport stdio
```

The server will print the connection message and registered tools to the Run window or terminal; use STDIO transport for local desktop clients and Copilot integrations that support STDIO.

### Claude Desktop / Claude Code

For Claude Desktop you can add a configuration entry so Claude will spawn the MCP process. Example JSON to add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["-m", "src.main", "--transport", "stdio"],
      "cwd": "/absolute/path/to/my-mcp-server"
    }
  }
}
```

If using a Claude Code / Cloud-based Claude connector that accepts an executable and args, use the same command but prefer `--transport sse` when the connector expects HTTP/SSE:

```bash
python -m src.main --transport sse
```

Notes:
- Replace `/absolute/path/to/my-mcp-server` with the repository path on your machine (for example `/home/you/projects/pp-task-runner-mcp`).
- The STDIO transport is appropriate for local desktop clients that communicate over stdin/stdout. Use the SSE transport for clients that communicate over HTTP/SSE.


## Claude Desktop Config

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["-m", "src.main", "--transport", "stdio"],
      "cwd": "/absolute/path/to/my-mcp-server"
    }
  }
}
```

## Structure

```
my-mcp-server/
├── src/
│   ├── tools/           # Tool definitions (@mcp.tool)
│   ├── resources/       # Resource definitions (@mcp.resource)
│   ├── prompts/         # Prompt templates (@mcp.prompt)
│   ├── config.py        # Configuration & env vars
│   ├── server.py        # FastMCP instance + lifespan
│   └── main.py          # Entrypoint
├── tests/
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Connection Message

On startup, the server prints to stderr:
```
✅ MCP Server connected and ready!
```
