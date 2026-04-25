PYTHON=python3
PYTHONPATH=src

.PHONY: run-menu
run-menu:
	@echo "Starting MCP menu..."
	@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m src.main --transport stdio

