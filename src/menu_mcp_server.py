"""Menu integration for the MCP server.

Tools registered:
- open_menu        — opens browser UI on first call; waits for next action on subsequent calls
- select_skill     — set active skill programmatically
- get_active_skill — return currently active skill
- list_skills      — return available skills as JSON
"""
import json
import os
import queue
import socket
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SKILLS = {
    "Greating": "**** Hello! Welcome to MCP! ****",
}

_MENU_TIMEOUT = 300


class _MenuState:
    def __init__(self):
        self.server: ThreadingHTTPServer | None = None
        self.events: queue.Queue = queue.Queue()
        self.lock = threading.Lock()


_menu = _MenuState()


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def _build_html(skills: dict) -> str:
    skill_buttons = "".join(
        f'<button class="skill-btn" onclick="pick(\'{name}\')">'
        f"<strong>{name}</strong><span>{desc}</span></button>"
        for name, desc in skills.items()
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Select Skill — Claude Code</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f5f5f5;
     display:flex;align-items:center;justify-content:center;min-height:100vh}}
.card{{background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.1);
       padding:32px;width:100%;max-width:480px}}
h1{{font-size:1.1em;color:#555;margin-bottom:20px;font-weight:500}}
.skill-btn{{display:block;width:100%;padding:14px 16px;margin:8px 0;
            border:1px solid #e0e0e0;border-radius:8px;background:#fff;
            cursor:pointer;text-align:left;font-size:.95em;transition:.15s}}
.skill-btn:hover{{background:#f0f7ff;border-color:#4a9eff}}
.skill-btn strong{{display:block}}
.skill-btn span{{display:block;font-size:.78em;color:#999;margin-top:3px}}
.exit-btn{{display:block;width:100%;padding:12px 16px;margin-top:16px;
           border:1px solid #ffcdd2;border-radius:8px;background:#fff;
           cursor:pointer;text-align:center;font-size:.9em;color:#e53935;transition:.15s}}
.exit-btn:hover{{background:#ffebee}}
#status{{margin-top:16px;font-size:.85em;color:#4a9eff;min-height:1.2em;text-align:center}}
</style>
</head>
<body>
<div class="card">
  <h1>Select a skill for Claude Code</h1>
  {skill_buttons}
  <button class="exit-btn" onclick="doExit()">Exit</button>
  <div id="status"></div>
</div>
<script>
async function post(body){{
  const r=await fetch('/action',{{method:'POST',
    headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});
  return r.json();
}}
async function pick(name){{
  document.getElementById('status').textContent='Running '+name+'…';
  try{{
    const d=await post({{action:'select',name}});
    document.getElementById('status').textContent=d.feedback||'✓ Done';
  }}catch{{document.getElementById('status').textContent='Error';}}
}}
async function doExit(){{
  document.getElementById('status').textContent='Closing…';
  try{{await post({{action:'exit',name:''}});}}catch{{}}
  window.close();
}}
window.addEventListener('beforeunload',()=>
  navigator.sendBeacon('/action',JSON.stringify({{action:'close',name:''}})));
</script>
</body>
</html>"""


def register_tools(mcp) -> None:
    selected_name = os.environ.get("MCP_SELECTED_NAME", "")
    selected_url = os.environ.get("MCP_SELECTED_URL", "")

    def open_menu() -> str:
        """Open browser skill menu (first call) or wait for next user action (subsequent calls).
        Returns JSON: action=greet → print message and call again; action=exit → print Goodbye and stop;
        action=close → browser closed by user, stop; action=timeout → no action within timeout, stop."""
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

                class _Handler(BaseHTTPRequestHandler):
                    def do_GET(self):
                        if self.path == "/":
                            body = _build_html(SKILLS).encode()
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

                        if action == "select" and name in SKILLS:
                            self._send_json({"feedback": "✓ Sent to Claude"})
                            _menu.events.put({"action": "greet", "name": name, "message": SKILLS[name]})

                        elif action == "exit":
                            self._send_json({"feedback": "Goodbye!"})
                            _menu.events.put({"action": "exit"})
                            self._schedule_shutdown()

                        elif action == "close":
                            # sendBeacon — no response body needed
                            self.send_response(200)
                            self.end_headers()
                            _menu.events.put({"action": "close"})
                            self._schedule_shutdown()

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

                    def _schedule_shutdown(self):
                        def _do():
                            time.sleep(0.3)
                            with _menu.lock:
                                server = _menu.server
                                _menu.server = None
                            if server:
                                server.shutdown()

                        threading.Thread(target=_do, daemon=True).start()

                    def log_message(self, *_):
                        pass

                server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
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


if __name__ == "__main__":
    from .mcp.server.fastmcp import FastMCP

    m = FastMCP("skill-menu-test")
    register_tools(m)
    m.run()