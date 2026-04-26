"""Web UI builder and HTTP handler factory for the menu package.

Supports simple menu-to-menu navigation via descriptions that start with
the prefix `MENU:<menu_name>`. If an option's description starts with
that prefix the UI will switch to the named menu; otherwise selecting
an option sends a greet event with the description as the message.
"""
import json
import time
import threading
from urllib.parse import urlparse, parse_qs
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .constants import DEFAULT_MENU
from .menu_renderer.components.button import _render_exit_button


def _build_html(options: dict, menu_name: str) -> str:
    option_buttons = "".join(
        f'<button class="skill-btn" onclick="pick(\'{name}\')">'
        f"<strong>{name}</strong><span>{desc}</span></button>"
        for name, desc in options.items()
    )
    display = "Main Menu" if menu_name == DEFAULT_MENU else menu_name
    title = f"PP Task Runner — {display}"
    # Only show Exit button on the default (root) menu — prefer shared renderer
    if menu_name == DEFAULT_MENU:
        if _render_exit_button:
            exit_button = _render_exit_button()
        else:
            exit_button = '<button class="exit-btn" onclick="doExit()">Exit</button>'
    else:
        exit_button = ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
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
  <h1>{title}</h1>
  {option_buttons}
  {exit_button}
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
    if(d.switch){{
      // navigate to the requested submenu
      window.location = '/?menu=' + encodeURIComponent(d.switch);
      return;
    }}
    document.getElementById('status').textContent=d.feedback||'✓ Done';
  }}catch{{document.getElementById('status').textContent='Error';}}
}}
async function doExit(){{
  document.getElementById('status').textContent='Closing…';
  try{{ await post({{action:'exit',name:''}}); }}catch{{}}
  // Ensure server receives a close event even if the fetch above is aborted
  try{{ navigator.sendBeacon('/action', JSON.stringify({{action:'close',name:''}})); }}catch{{}}
  // Try several strategies to close the window. Many browsers only allow
  // script-initiated windows to be closed programmatically; attempt a
  // self-replacement first then close. If that fails, navigate to about:blank
  // as a graceful fallback.
  try{{ window.open('','_self'); window.close(); return; }}catch{{}}
  try{{ window.close(); return; }}catch{{}}
  window.location.href = 'about:blank';
}}
// send a lightweight beacon on unload to help detect a real window close.
// Use action 'navigating' so the server can ignore it when the user is
// navigating between menus. This avoids shutting down the server during
// in-menu navigation while keeping the previous behavior of having a
// beacon present in the page.
window.addEventListener('beforeunload',() =>
  navigator.sendBeacon('/action',JSON.stringify({{action:'navigating',name:''}})));
</script>
</body>
</html>"""


def make_handler(all_menus: dict, menu_state) -> type:
    """Return a BaseHTTPRequestHandler subclass bound to the provided skills and menu_state.

    The returned handler will use the provided `menu_state` to post events
    to `menu_state.events` and to shut down the `menu_state.server` when needed.
    """

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                qs = parse_qs(parsed.query)
                menu_name = qs.get("menu", [DEFAULT_MENU])[0] or DEFAULT_MENU
                options = all_menus.get(menu_name, all_menus.get(DEFAULT_MENU, {}))
                body = _build_html(options, menu_name).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path == "/launch":
                # Launcher page: open the real menu in a script-created window
                # so that the child window is eligible to be closed by JS.
                qs = parse_qs(parsed.query)
                menu_name = qs.get("menu", [DEFAULT_MENU])[0] or DEFAULT_MENU
                launch_html_str = """<!doctype html><meta charset=utf-8>
<script>
  (function(){
    try{
      var menu = new URLSearchParams(location.search).get('menu')||'';
      var url = '/' + (menu?('?menu='+encodeURIComponent(menu)):'');
      var w = window.open(url, '_blank');
      // give the child a moment to open then try to close this launcher
      setTimeout(function(){ try{ window.close(); }catch(e){} }, 50);
    }catch(e){/* ignore */}
  })();
</script>"""
                launch_html = launch_html_str.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(launch_html)))
                self.end_headers()
                self.wfile.write(launch_html)
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
            options = all_menus.get(menu_name, all_menus.get(DEFAULT_MENU, {}))

            if action == "select" and name in options:
                desc = options.get(name, "")
                if isinstance(desc, str) and desc.startswith("MENU:"):
                    # navigation request — instruct client to switch menus
                    switch_to = desc.split(":", 1)[1]
                    self._send_json({"switch": switch_to})
                else:
                    self._send_json({"feedback": "✓ Sent to Claude"})
                    menu_state.events.put({"action": "greet", "name": name, "message": desc})

            elif action == "exit":
                self._send_json({"feedback": "Goodbye!"})
                menu_state.events.put({"action": "exit"})
                self._schedule_shutdown()

            elif action == "close":
                # sendBeacon — no response body needed
                self.send_response(200)
                self.end_headers()
                menu_state.events.put({"action": "close"})
                self._schedule_shutdown()

            elif action == "navigating":
                # client is navigating between pages on the same menu server;
                # ignore this and return 200 so the beacon doesn't cause a 400.
                self.send_response(200)
                self.end_headers()

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
                with menu_state.lock:
                    server = menu_state.server
                    menu_state.server = None
                if server:
                    server.shutdown()

            threading.Thread(target=_do, daemon=True).start()

        def log_message(self, *_):
            pass

    return _Handler

