PYTHON=python3
PYTHONPATH=src

.PHONY: run-menu simulate dev test

# Start the MCP server in stdio mode (waits for a client — use `simulate` instead for manual testing)
run-menu:
	@echo "Starting MCP server (stdio)…"
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.main --transport stdio

# Simulate Claude Code: spawns server.py, opens the browser menu, handles events
simulate:
	@$(PYTHON) simulate.py

# Open the MCP Inspector (browser GUI to call tools interactively)
dev:
	@echo "Opening MCP Inspector…"
	@PYTHONPATH=$(PYTHONPATH) mcp dev dev_server.py:mcp

# Run the automated test suite
test:
	@$(PYTHON) -m pytest -v