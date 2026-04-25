Call open_menu from the pp-task-runner MCP. It returns a JSON event — loop based on the action:
- {"action": "greet", "message": "..."} → print the message in the terminal, then call open_menu again to wait for the next action
- {"action": "exit"} → print "Goodbye !!!" in the terminal, stop
- {"action": "close"} → tell the user the browser was closed, stop
- {"action": "timeout"} → tell the user the menu timed out, stop