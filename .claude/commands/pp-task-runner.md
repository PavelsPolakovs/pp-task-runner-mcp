(Use the Monitor tool to run this command:
  python3 ./pp_task_runner.py

Set persistent=false, timeout_ms=300000, description="PP Task Runner — Main Menu".

The browser opens automatically. Claude Code stays free between events.

Each notification is a JSON line — handle it immediately when it arrives:
- {"action": "greet", "name": "...", "message": "..."} → print the message in the terminal
- {"action": "exit"} → print "Goodbye !!!" in the terminal
- {"action": "close"} → tell the user the browser was closed
- {"action": "timeout"} → tell the user the menu timed out

