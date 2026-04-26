"""Register MCP tools for opening and selecting tasks."""
import json
import os
import queue
import subprocess
import threading
import webbrowser
from urllib.parse import quote
from http.server import ThreadingHTTPServer

from .constants import DEFAULT_MENU, MENUS, _MENU_TIMEOUT
from .state import _free_port, _menu
from .web import make_handler


def register_tools(mcp) -> None:
    selected_name = os.environ.get("MCP_SELECTED_NAME", "")
    selected_url = os.environ.get("MCP_SELECTED_URL", "")

    def _open_menu_core(menu: str | None = None) -> dict:
        nonlocal selected_name, selected_url

        menu_name = menu or DEFAULT_MENU
        options = MENUS.get(menu_name, MENUS.get(DEFAULT_MENU, {}))

        with _menu.lock:
            if _menu.server is None:
                while not _menu.events.empty():
                    try:
                        _menu.events.get_nowait()
                    except queue.Empty:
                        break

                port = _free_port()
                Handler = make_handler(MENUS, _menu)
                server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
                _menu.server = server
                threading.Thread(target=server.serve_forever, daemon=True).start()
                # Create an inline launcher page (data: URL) that polls the
                # local server and opens the real menu in a script-created
                # window once the server is ready. Using a data: URL avoids
                # the race where the browser navigates to /launch before the
                # server starts and shows "page can't be found".
                launch_html = ('<!doctype html><meta charset=utf-8>\n'
                               '<script>\n'
                               '  (function(){\n'
                               '    const port = %d;\n'
                               '    const menu = %s;\n'
                               '    function tryOpen(){\n'
                               "      fetch('http://127.0.0.1:'+port+'/?menu='+encodeURIComponent(menu)).then(()=>{\n"
                               "        try{\n"
                               "          var url = 'http://127.0.0.1:'+port+'/?menu='+encodeURIComponent(menu);\n"
                               "          var w = window.open(url,'_blank','width=900,height=700');\n"
                               "          if(w){ try{w.focus()}catch(e){}; try{window.close()}catch(e){}; }\n"
                               "        }catch(e){}\n"
                               "      }).catch(()=>setTimeout(tryOpen,200));\n"
                               '    }\n'
                               '    tryOpen();\n'
                               '  })();\n'
                               '</script>') % (port, json.dumps(menu_name or ""))
                data_url = 'data:text/html;charset=utf-8,' + quote(launch_html)
                # Allow switching between 'launcher' (data: URL polling) and
                # 'direct' (open the HTTP URL immediately). Default to
                # direct mode to match user preference for reliable opening.
                mode = os.environ.get("MENU_OPEN_MODE", "direct").lower()
                try:
                    if mode == "direct":
                        direct_url = f"http://127.0.0.1:{port}/?menu={menu_name}"
                        print(f"Opening direct menu URL: {direct_url}", flush=True)
                        webbrowser.open(direct_url)
                    else:
                        print(f"Opening launcher (mode=launcher). Launcher URL shown below.", flush=True)
                        print(f"Menu launcher URL (open in browser if it didn't appear): {data_url}", flush=True)
                        print(f"Direct menu URL: http://127.0.0.1:{port}/?menu={menu_name}", flush=True)
                        webbrowser.open(data_url)
                except Exception:
                    # If webbrowser.open fails for any reason just print URLs
                    try:
                        print(f"Menu launcher URL: {data_url}", flush=True)
                        print(f"Direct menu URL: http://127.0.0.1:{port}/?menu={menu_name}", flush=True)
                    except Exception:
                        pass

        try:
            event = _menu.events.get(timeout=_MENU_TIMEOUT)
        except queue.Empty:
            event = {"action": "timeout"}

        if event.get("action") == "greet":
            selected_name = event["name"]
            selected_url = options.get(selected_name, "")

        return event

    def open_menu(menu: str | None = None) -> str:
        """Open the browser task menu and wait for the user's selection.

        Args:
            menu: Name of the menu to display. Defaults to the configured
                  default_menu (usually "main"). Pass "qa" to show the
                  testing/linting tasks defined in task_config.json.

        Returns a JSON string with one of these events:
          {"action": "greet", "name": "...", "message": "..."}
          {"action": "exit"}
          {"action": "close"}
          {"action": "timeout"}
        """
        return json.dumps(_open_menu_core(menu))

    def open_menu_dict(menu: str | None = None) -> dict:
        """Programmatic API: same as open_menu but returns a dict."""
        return _open_menu_core(menu)

    def select_skill(name: str, menu: str | None = None) -> str:
        """Activate a task by name without opening the browser.

        Args:
            name: Task name to activate.
            menu: Menu to search in (default: default_menu).
        """
        nonlocal selected_name, selected_url
        menu_name = menu or DEFAULT_MENU
        options = MENUS.get(menu_name, MENUS.get(DEFAULT_MENU, {}))
        if name not in options:
            available = ", ".join(options)
            return f"Unknown skill '{name}' in menu '{menu_name}'. Available: {available}"
        selected_name = name
        selected_url = options[name]
        return f"Activated: {name}"

    def get_active_skill() -> str:
        """Return the currently active task name and description."""
        if selected_name:
            return f"Active skill: {selected_name}\n{selected_url}"
        return "No skill selected. Call open_menu to choose one."

    def list_skills(menu: str | None = None) -> str:
        """Return available tasks as JSON.

        Args:
            menu: Menu name to list (default: default_menu).
                  Pass "qa" to list the QA/testing tasks.
        """
        menu_name = menu or DEFAULT_MENU
        options = MENUS.get(menu_name, MENUS.get(DEFAULT_MENU, {}))
        return json.dumps([{"name": n, "description": d} for n, d in options.items()])

    _REPO_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    def get_menu_command(menu: str | None = None) -> str:
        """Return the Monitor shell command to open the task menu non-blocking.

        Use this with the Monitor tool instead of open_menu to keep Claude
        free while waiting for browser input.

        Args:
            menu: Menu name (default: default_menu). Pass "qa" for QA tasks.

        Returns:
            Shell command string ready to pass to Monitor
            (persistent=false, timeout_ms=300000).

        Monitor event lines (one JSON per line on stdout):
          {"action": "greet", "name": "...", "message": "..."}
          {"action": "exit"}
          {"action": "close"}
        """
        # Run the menu server as a package so package-relative imports work:
        cmd = f"PYTHONPATH={_REPO_DIR}/src python3 -m menu_server"
        if menu:
            cmd += f" --menu {menu}"
        return cmd

    def update() -> str:
        """Pull latest changes from the remote repo (git pull).

        After a successful update reconnect the MCP server in Claude Code
        (/mcp → Reconnect) to reload the new code.
        """
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=_REPO_DIR,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = (result.stdout + result.stderr).strip()
            if result.returncode != 0:
                return f"git pull failed (exit {result.returncode}):\n{output}"
            return f"Updated successfully:\n{output}\n\nReconnect the MCP server to reload."
        except subprocess.TimeoutExpired:
            return "git pull timed out after 30 seconds."
        except Exception as e:
            return f"Error running git pull: {e}"

    mcp.tool()(get_menu_command)
    mcp.tool()(open_menu)
    mcp.tool()(open_menu_dict)
    mcp.tool()(select_skill)
    mcp.tool()(get_active_skill)
    mcp.tool()(list_skills)
    mcp.tool()(update)