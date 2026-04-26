"""Constants for the menu MCP package.

Defines TASKS (recommended name) and keeps SKILLS as an alias for
backwards compatibility with existing code/tests that import SKILLS.
"""

import json
import os

# Default tasks — can be overridden by `task_config.json` in the repo root.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_TASK_CONFIG = os.path.join(_REPO_ROOT, "task_config.json")

if os.path.exists(_TASK_CONFIG):
    try:
        with open(_TASK_CONFIG, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            TASKS = {t["name"]: t.get("description", "") for t in cfg.get("tasks", [])}
    except Exception:
        TASKS = {"Greating": "**** Hello! Welcome to MCP! ****"}
else:
    TASKS = {"Greating": "**** Hello! Welcome to MCP! ****"}

# Backwards compatibility: some modules/tests import SKILLS directly.
SKILLS = TASKS

# Default menu timeout (seconds)
_MENU_TIMEOUT = 300

