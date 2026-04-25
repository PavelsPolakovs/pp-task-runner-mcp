"""Server state and small utilities for the menu package."""
from http.server import ThreadingHTTPServer
import queue
import socket
import threading


class _MenuState:
    def __init__(self):
        # ThreadingHTTPServer | None
        self.server = None
        self.events: queue.Queue = queue.Queue()
        self.lock = threading.Lock()


_menu = _MenuState()


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]

