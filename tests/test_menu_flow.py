"""Integration tests for the open_menu → HTTP server → event flow.

open_menu starts a local HTTP server and waits for a browser action.
These tests mock `webbrowser.open` (so no real browser opens) and
send HTTP requests directly to simulate user interaction.
"""
import asyncio
import json
import threading
import time
import urllib.request
from unittest.mock import patch

from menu_mcp.constants import TASKS
from menu_mcp.state import _menu

FIRST_SKILL = next(iter(TASKS))


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


class TestOpenMenuFlow:
    def test_greet_event_on_skill_select(self, mcp_app):
        with patch("webbrowser.open"):
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()
            _post(port, {"action": "select", "name": FIRST_SKILL})
            t.join(timeout=5)

        assert results, "open_menu never returned"
        event = json.loads(results[0][1]["result"])
        assert event["action"] == "greet"
        assert event["name"] == FIRST_SKILL
        assert event["message"] == TASKS[FIRST_SKILL]

    def test_exit_event(self, mcp_app):
        with patch("webbrowser.open"):
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()
            _post(port, {"action": "exit", "name": ""})
            t.join(timeout=5)

        event = json.loads(results[0][1]["result"])
        assert event["action"] == "exit"

    def test_close_event(self, mcp_app):
        with patch("webbrowser.open"):
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()
            _post(port, {"action": "close", "name": ""})
            t.join(timeout=5)

        event = json.loads(results[0][1]["result"])
        assert event["action"] == "close"

    def test_html_page_served(self, mcp_app):
        with patch("webbrowser.open"):
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()

            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
                html = resp.read().decode()

            _post(port, {"action": "exit", "name": ""})
            t.join(timeout=5)

        assert "PP Task Runner — Main Menu" in html
        for skill_name in TASKS:
            assert skill_name in html

    def test_server_shuts_down_after_event(self, mcp_app):
        with patch("webbrowser.open"):
            t, results = _open_menu_in_thread(mcp_app)
            port = _wait_for_server()
            _post(port, {"action": "exit", "name": ""})
            t.join(timeout=5)

        # server should be stopped; a new connection must be refused
        time.sleep(0.5)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=2)
            assert False, "Server is still running after exit"
        except OSError:
            pass  # expected: connection refused