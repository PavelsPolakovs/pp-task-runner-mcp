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
```