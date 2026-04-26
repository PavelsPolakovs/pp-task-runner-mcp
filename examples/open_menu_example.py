"""Example: programmatic use of the menu_mcp API.

This shows how a project-consumer can call `open_menu(description=...)`
and handle the returned dict without using Monitor.
"""
from menu_mcp.tools import open_menu


def main():
    event = open_menu(description="Open main menu")
    action = event.get("action")
    if action == "greet":
        print("User chose:", event.get("name"))
        print("Message:", event.get("message"))
    elif action == "exit":
        print("Goodbye !!!")
    elif action == "close":
        print("Browser was closed by the user")
    elif action == "timeout":
        print("Menu timed out (no user action)")
    else:
        print("Unknown event:", event)


if __name__ == "__main__":
    main()

