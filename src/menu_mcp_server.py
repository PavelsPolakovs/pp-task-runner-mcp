"""Menu integration for the MCP server.

This module exposes `register_tools(mcp)` which will show an interactive
selection (using `questionary`) and register two tools on the provided
FastMCP instance:
- get_active_skill
- reopen_menu

The module also contains a tiny standalone runner for manual testing but the
preferred usage when running the server is to import this module and call
`register_tools(mcp)` from the server startup path so the menu appears when
the server starts.
"""
from typing import Tuple
import os
import sys
import threading
import questionary


SKILLS = {
    "Greating": "**** Hello! Welcome to MCP! ****",
}


def show_menu() -> Tuple[str, str]:
	"""Show the start menu and handle selections.

	The menu contains a single "Greating" item. When selected, the
	associated message is printed and the menu is shown again. The menu
	also provides an explicit "Exit" choice to finish and return to the
	caller.
	"""
	choices = list(SKILLS.keys()) + ["Exit"]

	while True:
		choice = questionary.select(
			"Выбери skill для Claude Code:",
			choices=choices,
		).ask()

		# None or empty or explicit Exit -> terminate the whole process so
		# the MCP server stops instead of continuing startup.
		if not choice or choice == "Exit":
			raise SystemExit(0)

		# Print the message for the selected skill and loop back to menu
		msg = SKILLS.get(choice)
		if msg:
			print(msg)
		else:
			print(f"Selected: {choice}")

		# continue loop to show menu again


def register_tools(mcp) -> None:
	"""Register menu-related tools on the given FastMCP instance.

	Behavior:
	- If the process has a TTY (sys.stdin.isatty()) the interactive
	  startup menu will be shown once to set the initial selection.
	- If there is no TTY (typical for automated/stdio-driven hosts like
	  some language-server/agent runners) the menu is NOT shown at
	  startup; tools are still registered and `reopen_menu` can be used
	  later to open the interactive menu on demand.

	You can force the menu at startup by setting environment variable
	`MCP_FORCE_MENU=1` but that will still fail if the platform doesn't
	provide a TTY for interactive prompts.
	"""

	# Default selection values
	selected_name = ""
	selected_url = ""

	# Allow pre-selecting a skill via environment variables (useful for
	# non-interactive hosts such as Claude Code when you cannot show a
	# TTY-based prompt). If provided, use it and skip the interactive menu.
	env_name = os.environ.get("MCP_SELECTED_NAME")
	env_url = os.environ.get("MCP_SELECTED_URL")
	if env_name:
		selected_name = env_name
		selected_url = env_url or ""

	# Decide whether to show the interactive menu now. If an env-based
	# selection was provided, prefer it and do not prompt.
	show_at_start = (os.environ.get("MCP_FORCE_MENU", "0") == "1" or sys.stdin.isatty()) and not selected_name

	if show_at_start:
		# If we are inside an event loop this will block; callers that run
		# the registration inside an executor should account for that.
		selected_name, selected_url = show_menu()

	# Define plain functions and register them with the provided mcp
	def get_active_skill() -> str:
		"""Return the currently selected skill URL."""
		if selected_url:
			return f"Execute the instructions from this URL: {selected_url}"
		return "No active skill selected. Call reopen_menu to choose one."

	def reopen_menu() -> str:
		"""Open the menu again and update the selected skill."""
		nonlocal selected_name, selected_url

		# show_menu() blocks on user input; run it in a thread if the
		# caller might be running inside an event loop or other managed
		# execution environment.
		def _run():
			try:
				new_name, new_url = show_menu()
				return new_name, new_url
			except SystemExit:
				# Propagate SystemExit to caller environment
				raise
			except Exception:
				return None, None

		# Run in a thread and wait for result
		t = threading.Thread(target=_run)
		t.daemon = True
		t.start()
		t.join()

		# After thread finished, call show_menu again in the main thread
		# to get the actual values (joining above ensures prompt completed).
		try:
			new_name, new_url = show_menu()
		except SystemExit:
			raise
		except Exception:
			new_name, new_url = None, None

		if new_name and new_url:
			selected_name, selected_url = new_name, new_url
			return f"Selected: {new_name} → {new_url}"
		return "Menu cancelled or failed."

	# Register tools on the provided FastMCP instance
	mcp.tool()(get_active_skill)
	mcp.tool()(reopen_menu)


if __name__ == "__main__":
	# Allow quick manual testing: create a local FastMCP and run it.
	from .mcp.server.fastmcp import FastMCP

	m = FastMCP("skill-menu-test")
	register_tools(m)
	m.run()


