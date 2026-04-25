## ---------------------------------------------------------------------------
# Makefile for pp-task-runner-mcp
# Organized by scope: Variables, Setup/Install, Run (foreground/background),
# Utilities and Help. Targets are documented inline. This Makefile assumes
# a POSIX-compatible shell (Linux/macOS). Override the Python interpreter by
# setting PYTHON when invoking make (e.g. `make start PYTHON=python`).
## ---------------------------------------------------------------------------

### Variables
PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
PROJECT_DIR := $(CURDIR)
OUT_DIR := $(PROJECT_DIR)/out
REQ_FILE := requirements.txt
SERVER_MODULE := src.main


### PHONY targets
.PHONY: help start run-stdio run-sse run-bg install-dev ensure-pip repo-summary clean


### Help / Documentation
help:
	@echo "pp-task-runner-mcp - Makefile targets"
	@echo ""
	@echo "Usage: make <target> [VARIABLE=value]"
	@echo ""
	@echo "Setup / Install targets:"
	@echo "  install-dev      Install Python dependencies from $(REQ_FILE)"
	@echo ""
	@echo "Run targets (server):"
	@echo "  start            Default: start the MCP server using stdio transport"
	@echo "  run-stdio        Run the server in the foreground with stdio transport"
	@echo "  run-sse          Run the server in the foreground with sse transport"
	@echo "  run-bg           Run the server in the background (nohup) and write logs to ./logs/mcp.log"
	@echo ""
	@echo "Utilities:"
	@echo "  repo-summary     Generate a repository summary into $(OUT_DIR)"
	@echo "  clean            Remove generated output (currently removes $(OUT_DIR))"
	@echo ""
	@echo "Examples:"
	@echo "  make install-dev"
	@echo "  make start"
	@echo "  make run-bg PYTHON=python"


### Default target: start the server using stdio
start: run-stdio


### Run (foreground)
# run-stdio: start the MCP server in the foreground using STDIO transport.
run-stdio:
	@echo "Starting MCP server (stdio) using $(PYTHON) - module $(SERVER_MODULE)"
	$(PYTHON) -m $(SERVER_MODULE) --transport stdio


# run-sse: start the MCP server in the foreground using SSE transport.
run-sse:
	@echo "Starting MCP server (sse) using $(PYTHON) - module $(SERVER_MODULE)"
	$(PYTHON) -m $(SERVER_MODULE) --transport sse


### Run (background)
# run-bg: start server in background using nohup and write logs to ./logs/mcp.log.
# Note: This is a convenience for development. Use a process manager for
# production (systemd, supervisord, docker, etc.).
run-bg:
	@mkdir -p logs
	@echo "Starting MCP server in background (logs/mcp.log). Use 'pgrep -f \"-m $(SERVER_MODULE)\"' to find PID."
	@nohup $(PYTHON) -m $(SERVER_MODULE) --transport stdio > logs/mcp.log 2>&1 &
	@sleep 0.2
	@echo "Background server started; tail -n 50 logs/mcp.log to view recent output."


### Setup / Install
install-dev:
	@echo "Installing development dependencies from $(REQ_FILE) using $(PIP)"
	# Ensure pip is available for the selected Python interpreter.
	@$(MAKE) ensure-pip PYTHON=$(PYTHON) PIP="$(PIP)"
	@$(PIP) install -r $(REQ_FILE)


### Ensure pip is available for $(PYTHON)
ensure-pip:
	@echo "Ensuring pip is available for $(PYTHON)"
	@bash $(PROJECT_DIR)/scripts/ensure_pip.sh $(PYTHON) "$(PIP)"


### Utilities
repo-summary:
	@echo "Generating repository summary into $(OUT_DIR)"
	$(PYTHON) $(PROJECT_DIR)/scripts/generate_repo_summary.py --repo $(PROJECT_DIR) --out-dir $(OUT_DIR)


clean:
	@echo "Cleaning $(OUT_DIR)"
	@rm -rf $(OUT_DIR)
