"""Additional HTTP/integration tests for the menu web UI.

These tests exercise headers, browser open call, error handling and shutdown
behavior of the HTTP handler returned by `menu_mcp.web.make_handler`.
"""
import asyncio
import json
import threading
import time
import urllib.request
import urllib.error
from unittest.mock import patch

from menu_mcp.constants import TASKS
from menu_mcp.state import _menu


def _post(port: int, payload: dict) -> dict | None:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/action",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _wait_for_server(timeout: float = 3.0) -> int:
    """Poll until _menu.server is ready and return its port."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with _menu.lock:
            server = _menu.server
        if server:
            return server.server_address[1]
        time.sleep(0.05)
    raise TimeoutError("HTTP server did not start in time")


def _run(app, tool, **kwargs):
    return asyncio.run(app.call_tool(tool, kwargs))


def _open_menu_in_thread(app):
    """Run open_menu in a background thread; return results list."""
    results = []
    t = threading.Thread(target=lambda: results.append(_run(app, "open_menu")), daemon=True)
    t.start()
    return t, results


class TestMenuHTTP:
    def test_browser_open_called(self, mcp_app):
        with patch("webbrowser.open") as mock_open:
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()

            # webbrowser.open should be invoked; allow either a direct URL or
            # our data: launcher URL used to avoid races when starting the
            # server (see implementation notes).
            assert mock_open.called
            called_url = mock_open.call_args[0][0]
            assert called_url.startswith(f"http://127.0.0.1:{port}") or called_url.startswith("data:text/html"), called_url

            # shut down cleanly
            _post(port, {"action": "exit", "name": ""})
            t.join(timeout=5)

    def test_html_headers_and_structure(self, mcp_app):
        with patch("webbrowser.open"):
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()

            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
                content_type = resp.getheader("Content-Type")
                content_length = resp.getheader("Content-Length")
                body = resp.read().decode()

            # sanity checks on headers and content
            assert content_type and "text/html" in content_type
            assert content_type and "charset=utf-8" in content_type
            # Content-Length is the byte length of the encoded body
            assert content_length == str(len(body.encode("utf-8")))
            assert "PP Task Runner — Main Menu" in body
            assert 'class="skill-btn"' in body
            assert "doExit()" in body
            assert "navigator.sendBeacon" in body

            _post(port, {"action": "exit", "name": ""})
            t.join(timeout=5)

    def test_unknown_action_returns_400(self, mcp_app):
        with patch("webbrowser.open"):
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()

            body = json.dumps({"action": "bogus"}).encode()
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/action",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                urllib.request.urlopen(req, timeout=5)
                assert False, "Request should have returned 400"
            except urllib.error.HTTPError as e:
                assert e.code == 400

            _post(port, {"action": "exit", "name": ""})
            t.join(timeout=5)

    def test_select_unknown_skill_returns_400(self, mcp_app):
        with patch("webbrowser.open"):
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()

            body = json.dumps({"action": "select", "name": "nope"}).encode()
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/action",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                urllib.request.urlopen(req, timeout=5)
                assert False, "Request should have returned 400 for unknown skill"
            except urllib.error.HTTPError as e:
                assert e.code == 400

            _post(port, {"action": "exit", "name": ""})
            t.join(timeout=5)

    def test_close_triggers_shutdown(self, mcp_app):
        with patch("webbrowser.open"):
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()
            _post(port, {"action": "close", "name": ""})
            t.join(timeout=5)

        # server should be stopped; a new connection must be refused
        time.sleep(0.5)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2)
            assert False, "Server is still running after close"
        except OSError:
            pass  # expected: connection refused

