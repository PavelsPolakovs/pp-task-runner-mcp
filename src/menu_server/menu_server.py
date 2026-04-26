#!/usr/bin/env python3
"""Standalone menu HTTP server. Prints JSON events to stdout (one line each).
Designed to be run via Monitor so Claude Code receives events as notifications.

Usage:
    python3 src/menu_server/menu_server.py              # shows the default (main) menu
    python3 src/menu_server/menu_server.py --menu qa    # shows the QA/testing menu
"""
import argparse
import json
import html
import os
import socket
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# Load menus from the package so task_config.json is the single source of truth.
# When running the package (`python -m menu_server`) or with PYTHONPATH=src this
# import will resolve normally.
from menu_mcp.constants import DEFAULT_MENU, MENUS  # noqa: E402

_TIMEOUT = 300
_done = threading.Event()


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]
# Import the renderer using a package-relative import. When running via
# `python -m menu_server` or when `src` is on PYTHONPATH this works
# consistently. The previous fallback path-loading is no longer necessary.
from .menu_renderer import render_menu_html


def _emit(event: dict):
    print(json.dumps(event), flush=True)


def _make_handler(tasks: dict):
    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                qs = parse_qs(parsed.query)
                menu_name = qs.get("menu", [DEFAULT_MENU])[0] or DEFAULT_MENU
                options = MENUS.get(menu_name, MENUS.get(DEFAULT_MENU, {}))
                body = render_menu_html(options, menu_name).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                # Allow CORS requests from the launcher (data: origin)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if self.path != "/action":
                self.send_response(404)
                self.end_headers()
                return

            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            action = payload.get("action", "")
            name = payload.get("name", "")

            # Determine originating menu from Referer (contains ?menu=...)
            referer = self.headers.get("Referer", "/")
            parsed_ref = urlparse(referer)
            menu_name = parse_qs(parsed_ref.query).get("menu", [DEFAULT_MENU])[0] or DEFAULT_MENU
            options = MENUS.get(menu_name, MENUS.get(DEFAULT_MENU, {}))

            if action == "select" and name in options:
                desc = options.get(name, "")
                if isinstance(desc, str) and desc.startswith("MENU:"):
                    switch_to = desc.split(":", 1)[1]
                    self._send_json({"switch": switch_to})
                else:
                    self._send_json({"feedback": "✓ Sent to Claude"})
                    _emit({"action": "greet", "name": name, "message": desc})

            elif action == "exit":
                self._send_json({"feedback": "Goodbye!"})
                _emit({"action": "exit"})
                threading.Thread(
                    target=lambda: (time.sleep(0.3), _done.set()), daemon=True
                ).start()

            elif action == "close":
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                _emit({"action": "close"})
                _done.set()

            elif action == "navigating":
                # Ignore ephemeral beacons sent during in-page navigation.
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

            else:
                self.send_response(400)
                self.end_headers()

        def _send_json(self, data: dict):
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def log_message(self, *_):
            pass

    return _Handler


def main(argv: list | None = None) -> int:
    """Run the standalone menu HTTP server.

    Args:
        argv: Optional list of command-line arguments (for testing). If None,
              uses sys.argv.

    Returns:
        Exit code (0 on success).
    """
    parser = argparse.ArgumentParser(description="PP Task Runner standalone menu server")
    parser.add_argument(
        "--menu",
        default=DEFAULT_MENU,
        help=f"Menu name to display (default: {DEFAULT_MENU!r}). Available: {', '.join(MENUS)}",
    )
    args = parser.parse_args(argv)

    tasks = MENUS.get(args.menu, MENUS.get(DEFAULT_MENU, {}))

    port = _free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), _make_handler(tasks))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    # Open via a small launcher page so the real menu is opened in a
    # script-created window. That makes the child window eligible to be
    # closed programmatically by the Exit button in most browsers.
    try:
        from urllib.parse import quote

        # Build a data: URL launcher that polls the server and opens the
        # real menu in a script-created window once ready. This avoids a
        # race where the browser requests /launch before the server is
        # accepting connections and shows a DNS/connection error page.
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
                       '</script>') % (port, json.dumps(args.menu or ''))
        data_url = 'data:text/html;charset=utf-8,' + quote(launch_html)
    except Exception:
        data_url = f"http://127.0.0.1:{port}/launch?menu={quote(args.menu or '')}"
    # Print helpful URLs so a developer can open the menu manually if the
    # system's default browser does not launch automatically.
    # Allow switching between 'launcher' and 'direct' via environment
    # variable MENU_OPEN_MODE. Default to direct to open the HTTP URL
    # immediately (less race-prone on many systems).
    mode = os.environ.get("MENU_OPEN_MODE", "direct").lower()
    try:
        if mode == "direct":
            direct_url = f"http://127.0.0.1:{port}/?menu={args.menu}"
            print(f"Opening direct menu URL: {direct_url}", flush=True)
            webbrowser.open(direct_url)
        else:
            print(f"Opening launcher (mode=launcher). Launcher URL shown below.", flush=True)
            print(f"Menu launcher URL (open in browser if it didn't appear): {data_url}", flush=True)
            print(f"Direct menu URL: http://127.0.0.1:{port}/?menu={args.menu}", flush=True)
            webbrowser.open(data_url)
    except Exception:
        try:
            print(f"Menu launcher URL: {data_url}", flush=True)
            print(f"Direct menu URL: http://127.0.0.1:{port}/?menu={args.menu}", flush=True)
        except Exception:
            pass
    _done.wait(timeout=_TIMEOUT)
    server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

