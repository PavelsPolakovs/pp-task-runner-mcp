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


def _menu_styles() -> str:
    """Return the CSS used by the menu page."""
    return (
        "*{box-sizing:border-box;margin:0;padding:0}"
        "body{font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;background:#f5f5f5;"
        "display:flex;align-items:center;justify-content:center;min-height:100vh}"
        ".card{background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.1);"
        "padding:32px;width:100%;max-width:480px}"
        "h1{font-size:1.1em;color:#555;margin-bottom:20px;font-weight:500}"
        ".skill-btn{display:block;width:100%;padding:14px 16px;margin:8px 0;"
        "border:1px solid #e0e0e0;border-radius:8px;background:#fff;"
        "cursor:pointer;text-align:left;font-size:.95em;transition:.15s}"
        ".skill-btn:hover{background:#f0f7ff;border-color:#4a9eff}"
        ".skill-btn strong{display:block}"
        ".skill-btn span{display:block;font-size:.78em;color:#999;margin-top:3px}"
        ".exit-btn{display:block;width:100%;padding:12px 16px;margin-top:16px;"
        "border:1px solid #ffcdd2;border-radius:8px;background:#fff;"
        "cursor:pointer;text-align:center;font-size:.9em;color:#e53935;transition:.15s}"
        ".exit-btn:hover{background:#ffebee}"
        "#status{margin-top:16px;font-size:.85em;color:#4a9eff;min-height:1.2em;text-align:center}"
    )


def _render_skill_button(name: str, description: str) -> str:
    """Render a single skill button.

    Uses a data-name attribute (HTML-escaped) and escapes visible text.
    """
    label_html = html.escape(name)
    desc_html = html.escape(description)
    data_name = html.escape(name, quote=True)
    return (
        f'<button class="skill-btn" data-name="{data_name}" '
        f'onclick="pick(this.dataset.name)">'  # pick will read dataset
        f"<strong>{label_html}</strong><span>{desc_html}</span></button>"
    )


def _render_exit_button() -> str:
    return '<button class="exit-btn" onclick="doExit()">Exit</button>'


def _render_status_div() -> str:
    return '<div id="status"></div>'


def _render_script() -> str:
    """Return the JavaScript for the page as a single string."""
    return (
        "async function post(body){"
        "const r=await fetch('/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});"
        "return r.json();}"
        "async function pick(name){"
        "document.getElementById('status').textContent='Running '+name+'…';"
        "try{const d=await post({action:'select',name});document.getElementById('status').textContent=d.feedback||'✓ Done';}"
        "catch{document.getElementById('status').textContent='Error';}}"
        "async function doExit(){document.getElementById('status').textContent='Closing…';"
        "try{await post({action:'exit',name:''});}catch{}window.close();}"
        "window.addEventListener('beforeunload',()=>navigator.sendBeacon('/action',JSON.stringify({action:'close',name:''})));"
    )


def _build_html(skills: dict) -> str:
    skill_buttons = "".join(_render_skill_button(name, desc) for name, desc in skills.items())
    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html lang=\"en\">")
    html_parts.append("<head>")
    html_parts.append("<meta charset=\"utf-8\">")
    html_parts.append("<title>PP Task Runner — Main Menu</title>")
    html_parts.append("<style>")
    html_parts.append(_menu_styles())
    html_parts.append("</style>")
    html_parts.append("</head>")
    html_parts.append("<body>")
    html_parts.append('<div class="card">')
    html_parts.append("  <h1>PP Task Runner — Main Menu</h1>")
    html_parts.append(skill_buttons)
    html_parts.append(_render_exit_button())
    html_parts.append(_render_status_div())
    html_parts.append("</div>")
    html_parts.append("<script>")
    html_parts.append(_render_script())
    html_parts.append("</script>")
    html_parts.append("</body>")
    html_parts.append("</html>")
    return "\n".join(html_parts)


def _emit(event: dict):
    print(json.dumps(event), flush=True)


def _make_handler(skills: dict):
    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                body = _build_html(skills).encode()
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

            if action == "select" and name in skills:
                self._send_json({"feedback": "✓ Sent to Claude"})
                _emit({"action": "greet", "name": name, "message": skills[name]})

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

    skills = MENUS.get(args.menu, MENUS.get(DEFAULT_MENU, {}))

    port = _free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), _make_handler(skills))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}")
    _done.wait(timeout=_TIMEOUT)
    server.shutdown()
    sys.exit(0)

