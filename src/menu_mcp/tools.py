"""Register MCP tools for opening and selecting skills.

This module implements `register_tools(mcp)` by reusing the smaller
components in this package.
"""
import json
import os
import queue
import threading
import webbrowser
from http.server import ThreadingHTTPServer

from .constants import SKILLS, _MENU_TIMEOUT
from .state import _menu, _free_port
from .web import make_handler


def register_tools(mcp) -> None:
    selected_name = os.environ.get("MCP_SELECTED_NAME", "")
    selected_url = os.environ.get("MCP_SELECTED_URL", "")

    def open_menu() -> str:
        """Open browser skill menu (first call) or wait for next user action.

        Returns JSON describing the event, e.g. action=greet/exit/close/timeout
        """
        nonlocal selected_name, selected_url

        with _menu.lock:
            if _menu.server is None:
                # Clear stale events from any previous session
                while not _menu.events.empty():
                    try:
                        _menu.events.get_nowait()
                    except queue.Empty:
                        break

                port = _free_port()
                Handler = make_handler(SKILLS, _menu)

                server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
                _menu.server = server
                threading.Thread(target=server.serve_forever, daemon=True).start()
                webbrowser.open(f"http://127.0.0.1:{port}")

        try:
            event = _menu.events.get(timeout=_MENU_TIMEOUT)
        except queue.Empty:
            event = {"action": "timeout"}

        if event.get("action") == "greet":
            selected_name = event["name"]
            selected_url = SKILLS.get(selected_name, "")

        return json.dumps(event)

    def select_skill(name: str) -> str:
        """Set the active skill by name."""
        nonlocal selected_name, selected_url
        if name not in SKILLS:
            return f"Unknown skill '{name}'. Available: {', '.join(SKILLS)}"
        selected_name = name
        selected_url = SKILLS[name]
        return f"Activated: {name}"

    def get_active_skill() -> str:
        """Return the currently active skill."""
        if selected_name:
            return f"Active skill: {selected_name}\n{selected_url}"
        return "No skill selected. Call open_menu to choose one."

    def list_skills() -> str:
        """Return available skills as JSON."""
        return json.dumps([{"name": n, "description": d} for n, d in SKILLS.items()])

    mcp.tool()(open_menu)
    mcp.tool()(select_skill)
    mcp.tool()(get_active_skill)
    mcp.tool()(list_skills)

