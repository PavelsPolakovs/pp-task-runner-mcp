"""Single source of truth for all menu definitions.

Config is loaded from ``src/menu_mcp/task_config.json`` (package-local).

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

# Always prefer the package-local configuration file. The repository-root
# copy was removed; keep the code simple and load config from the package.
_PACKAGE_TASK_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "task_config.json")
_TASK_CONFIG = _PACKAGE_TASK_CONFIG

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