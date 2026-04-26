#!/usr/bin/env python3
"""Simulate Claude Code running /start-pp-task-runner (Monitor approach).

Runs the standalone menu server under `src/menu_server/menu_server.py` as a subprocess
and reads each JSON event from its stdout as it arrives — identical to how Claude
Code's Monitor tool handles it.

Usage:
    python3 simulate.py
    make simulate
"""
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
# Run menu server as a module so package-relative imports work reliably.
MENU_MODULE = "menu_server"


def handle(event: dict) -> None:
    action = event.get("action")
    if action == "greet":
        print(event["message"])
    elif action == "exit":
        print("Goodbye !!!")
    elif action == "close":
        print("Browser was closed.")
    else:
        print(f"Unknown event: {event}")


def main() -> None:
    print("pp-task-runner simulator — press Ctrl+C to quit\n")

    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(REPO_ROOT, "src")
    proc = subprocess.Popen(
        [sys.executable, "-m", MENU_MODULE],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                print(f"[raw] {line}")
                continue
            handle(event)
    except KeyboardInterrupt:
        proc.terminate()
        print("\nStopped.")
    finally:
        proc.wait()


if __name__ == "__main__":
    main()