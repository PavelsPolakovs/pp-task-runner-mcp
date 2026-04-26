PYTHON=python3
PYTHONPATH=src

.PHONY: up dev test

# Simulate Claude Code: spawns server.py, opens the browser menu, handles events
up:
	@echo "Starting simulator (spawns menu_server.py and handles events)…"
	@$(PYTHON) simulate.py

# Open the MCP Inspector (browser GUI to call tools interactively)
dev:
	@echo "Opening MCP Inspector…"
	@PYTHONPATH=$(PYTHONPATH) mcp dev dev_server.py:mcp

# Run the automated test suite
test:
	@$(PYTHON) -m pytest -v