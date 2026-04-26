#!/usr/bin/env python3
"""Deprecated: top-level menu_server.py removed.

This file was intentionally removed — the standalone server now lives at
`src/menu_server/menu_server.py`. Please run that file directly or use the
`pp_task_runner.py` entrypoint:

	python3 src/menu_server/menu_server.py
	python3 pp_task_runner.py

If you have scripts invoking `menu_server.py` from the repository root, update
them to the new path. This placeholder exits with a helpful message.
"""
import sys

sys.exit(
	"menu_server.py has been removed from the repository root. "
	"Use 'python3 src/menu_server/menu_server.py' or 'python3 pp_task_runner.py'."
)
