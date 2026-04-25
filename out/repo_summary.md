# pp-task-runner-mcp

## Entrypoint

- module: `src.main`
- function: `main`
- source: `/home/polakovs/PhpstormProjects/pp-task-runner-mcp/src/main.py`

## Dependencies

- `mcp[cli]>=1.0.0`
- `python-dotenv>=1.0.0`

## Detected MCP artifacts

## Tests

- files: 2
- `tests/__init__.py`
- `tests/test_server.py`

## Run instructions (excerpt from README)

```
# my-mcp-server

Initial MCP (Model Context Protocol) server structure using FastMCP.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
# STDIO transport (Claude Desktop, Cursor, etc.)
python -m src.main --transport stdio

# SSE transport (HTTP-based clients)
python -m src.main --transport sse
```

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

The server will print the connection message and registered tools to the Run
```