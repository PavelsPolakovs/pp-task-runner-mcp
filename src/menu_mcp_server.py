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

	This shows the menu once at registration time to set the initial
	selection.
	"""
	selected_name, selected_url = show_menu()

	# Define plain functions and register them with the provided mcp using
	# the decorator factory returned by `mcp.tool()`.
	def get_active_skill() -> str:
		"""Return the currently selected skill URL."""
		return f"Execute the instructions from this URL: {selected_url}"

	def reopen_menu() -> str:
		"""Open the menu again and update the selected skill."""
		nonlocal selected_name, selected_url
		new_name, new_url = show_menu()
		selected_name, selected_url = new_name, new_url
		return f"Selected: {new_name} → {new_url}"

	# Register tools on the provided FastMCP instance
	mcp.tool()(get_active_skill)
	mcp.tool()(reopen_menu)


if __name__ == "__main__":
	# Allow quick manual testing: create a local FastMCP and run it.
	from .mcp.server.fastmcp import FastMCP

	m = FastMCP("skill-menu-test")
	register_tools(m)
	m.run()


