Call open_menu from the pp-task-runner MCP. It returns a JSON event — handle it:
- {"action": "greet", "name": "...", "message": "..."} → print the message in the terminal, stop
- {"action": "exit"} → print "Goodbye !!!" in the terminal, stop
- {"action": "close"} → tell the user the browser was closed, stop
- {"action": "timeout"} → tell the user the menu timed out, stop