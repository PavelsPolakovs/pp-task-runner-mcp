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

# Load menus from the package so task_config.json is the single source of truth.
# When this file lives under src/menu_server/, ensure repo/src is on sys.path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
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
            if self.path == "/":
                body = render_menu_html(tasks).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
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

            if action == "select" and name in tasks:
                self._send_json({"feedback": "✓ Sent to Claude"})
                _emit({"action": "greet", "name": name, "message": tasks[name]})

            elif action == "exit":
                self._send_json({"feedback": "Goodbye!"})
                _emit({"action": "exit"})
                threading.Thread(
                    target=lambda: (time.sleep(0.3), _done.set()), daemon=True
                ).start()

            elif action == "close":
                self.send_response(200)
                self.end_headers()
                _emit({"action": "close"})
                _done.set()

            else:
                self.send_response(400)
                self.end_headers()

        def _send_json(self, data: dict):
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    return _Handler


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PP Task Runner standalone menu server")
    parser.add_argument(
        "--menu",
        default=DEFAULT_MENU,
        help=f"Menu name to display (default: {DEFAULT_MENU!r}). Available: {', '.join(MENUS)}",
    )
    args = parser.parse_args()

    tasks = MENUS.get(args.menu, MENUS.get(DEFAULT_MENU, {}))

    port = _free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), _make_handler(tasks))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}")
    _done.wait(timeout=_TIMEOUT)
    server.shutdown()
    sys.exit(0)

