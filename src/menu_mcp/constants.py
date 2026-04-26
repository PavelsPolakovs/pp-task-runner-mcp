"""Single source of truth for all menu definitions.

Config is loaded from ``task_config.json`` at the repository root.

New format (named menus)::

    {
      "default_menu": "main",
      "menus": {
        "main": [{"name": "make up", "description": "..."}],
        "qa":   [{"name": "Run tests", "description": "..."}]
      }
    }

Legacy format (flat list) is still supported — tasks are placed in a
synthetic "main" menu::

    {"tasks": [{"name": "...", "description": "..."}]}

Exports
-------
MENUS       dict[str, dict[str, str]]  - all named menus
DEFAULT_MENU str                        - name of the default menu
TASKS       dict[str, str]             - alias for MENUS[DEFAULT_MENU]
_MENU_TIMEOUT int                      - seconds to wait for a browser action
"""

import json
import os

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_TASK_CONFIG = os.path.join(_REPO_ROOT, "task_config.json")

_FALLBACK: dict[str, dict[str, str]] = {
    "main": {"Greating": "**** Hello! Welcome to MCP! ****"}
}

MENUS: dict[str, dict[str, str]] = {}
DEFAULT_MENU: str = "main"

if os.path.exists(_TASK_CONFIG):
    try:
        with open(_TASK_CONFIG, "r", encoding="utf-8") as _f:
            _cfg = json.load(_f)

        if "menus" in _cfg:
            MENUS = {
                menu_name: {t["name"]: t.get("description", "") for t in tasks}
                for menu_name, tasks in _cfg["menus"].items()
            }
            DEFAULT_MENU = _cfg.get("default_menu", "main")
        elif "tasks" in _cfg:
            MENUS = {"main": {t["name"]: t.get("description", "") for t in _cfg["tasks"]}}
    except Exception:
        pass

if not MENUS:
    MENUS = _FALLBACK

# TASKS is the canonical mapping for the default menu
TASKS = MENUS.get(DEFAULT_MENU, next(iter(MENUS.values())))

_MENU_TIMEOUT = 300