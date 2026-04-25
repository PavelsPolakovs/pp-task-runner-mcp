import asyncio
import inspect
import sys
from contextlib import asynccontextmanager
from typing import Callable, Any, Dict

# Detect prompt_toolkit availability early so we can show a helpful
# message if it's missing instead of silently falling back.
try:
    import prompt_toolkit  # noqa: F401
    _HAS_PROMPT_TOOLKIT = True
except Exception:
    _HAS_PROMPT_TOOLKIT = False


class FastMCP:
    """A minimal stand-in for the real FastMCP used by the project.

    This implementation supports registering tools via the `@mcp.tool()`
    decorator and provides a `run(transport=...)` method that invokes
    the repository's lifespan and demonstrates calling registered tools.
    """

    def __init__(self, name: str, lifespan: Callable = None):
        self.name = name
        self.lifespan = lifespan
        self._tools: Dict[str, Callable] = {}

    def tool(self, *dargs, **dkwargs):
        """Decorator to register a coroutine function as a tool."""

        def decorator(fn: Callable):
            self._tools[fn.__name__] = fn
            return fn

        # Support being used as `@mcp.tool()` with or without args
        if len(dargs) == 1 and callable(dargs[0]):
            return decorator(dargs[0])
        return decorator

    async def _run_async(self, transport: str):
        # If a lifespan asynccontextmanager was provided, enter it.
        if self.lifespan is not None:
            try:
                async with self.lifespan(self):
                    await self._after_start(transport)
            except Exception as e:
                print(f"[FastMCP shim] lifespan raised: {e}")
        else:
            await self._after_start(transport)

    async def _after_start(self, transport: str):
        print(f"[FastMCP shim] Server '{self.name}' running with transport={transport}")
        if self._tools:
            print("[FastMCP shim] Registered tools:")
            for name, fn in self._tools.items():
                sig = str(inspect.signature(fn)) if inspect.iscoroutinefunction(fn) else "()"
                print(f" - {name}{sig}")
        else:
            print("[FastMCP shim] No tools registered")

        # Demonstrate calling a `hello` tool if present
        if "hello" in self._tools:
            fn = self._tools["hello"]
            try:
                if inspect.iscoroutinefunction(fn):
                    res = await fn("World")
                else:
                    res = fn("World")
                print(f"[FastMCP shim] hello('World') -> {res}")
            except Exception as e:
                print(f"[FastMCP shim] calling hello failed: {e}")

        # For stdio transport, present a simple start menu and keep the
        # server running until the user chooses to exit. This simulates an
        # interactive session for development/testing.
        if transport == "stdio":
            print("[FastMCP shim] (stdio) interactive start menu")

            async def ainput(prompt: str = "") -> str:
                """Asynchronous wrapper around blocking input(). Uses
                asyncio.to_thread for Python 3.9+ to run input in a thread.
                Falls back to simple input() when stdin is not a tty.
                """
                try:
                    return await asyncio.to_thread(input, prompt)
                except EOFError:
                    # Treat EOF (Ctrl-D) as an exit command
                    return ""  # return empty string which we'll treat as exit

            # Try to use prompt_toolkit for a cross-platform, themed interactive
            # menu. If prompt_toolkit is unavailable or stdin is not a TTY, fall
            # back to the simple line-based input fallback.

            async def _prompt_toolkit_menu() -> str:
                """Return 'greeting', 'exit', or None if cancelled/not available."""
                if not _HAS_PROMPT_TOOLKIT:
                    # Inform the user once about missing dependency and
                    # fall back to the line-input prompt.
                    print(
                        "[FastMCP shim] prompt_toolkit is not installed; to get the interactive menu install: pip install -r requirements.txt",
                        file=sys.stderr,
                    )
                    return None

                try:
                    from prompt_toolkit.shortcuts import radiolist_dialog
                    from prompt_toolkit.styles import Style
                except Exception:
                    return None

                style = Style.from_dict({
                    # Use bright cyan for focused text and bold
                    'radio-selected': 'fg:ansicyan bold',
                    'radio': 'fg:ansiwhite',
                })

                # radiolist_dialog is synchronous; run it in a thread to avoid
                # blocking the asyncio loop.
                try:
                    result = await asyncio.to_thread(
                        radiolist_dialog,
                        title="MCP Start Menu",
                        text="Select an option:",
                        values=[('greeting', 'Greeting'), ('exit', 'Exit')],
                        style=style,
                    )
                    return result
                except Exception:
                    return None

            # If stdin isn't a TTY, use the old line-input fallback
            tty_mode = sys.stdin.isatty()

            # If we're in an interactive TTY but prompt_toolkit is missing,
            # fail fast so the developer notices and installs dependencies.
            if tty_mode and not _HAS_PROMPT_TOOLKIT:
                print(
                    "[FastMCP shim] interactive menu requires prompt_toolkit.\n"
                    "Install dependencies and try again:\n  python3 -m pip install -r requirements.txt",
                    file=sys.stderr,
                )
                # Exit so the server doesn't silently fall back to a less
                # capable prompt when an interactive UI was expected.
                raise SystemExit(2)

            while True:
                try:
                    if tty_mode:
                        selection = await _prompt_toolkit_menu()
                        if selection is None:
                            # Either user cancelled or prompt_toolkit missing;
                            # fall back to line input.
                            choice = (await ainput("Choose an option [1-2 or name]: ")).strip()
                        else:
                            if selection == 'greeting':
                                choice = '1'
                            elif selection == 'exit':
                                choice = '2'
                            else:
                                choice = str(selection)
                    else:
                        choice = (await ainput("Choose an option [1-2 or name]: ")).strip()

                    # Interpret choice
                    if choice == "1" or (isinstance(choice, str) and choice.lower() in ("g", "greeting")):
                        print("**** Hello! Welcome to MCP! ****")
                        await asyncio.sleep(0)
                        continue

                    if choice == "2" or (isinstance(choice, str) and choice.lower() in ("exit", "e", "")):
                        print("Goodbye! Shutting down MCP server.")
                        break

                    # Unknown input -> re-prompt
                    print(f"Unrecognized choice: '{choice}'. Please enter 1 or 2 or use the menu.")
                except Exception as e:
                    print(f"[FastMCP shim] menu error: {e}")
                    break
        else:
            # SSE or others: short sleep then exit
            await asyncio.sleep(1)

    def run(self, transport: str = "stdio"):
        try:
            asyncio.run(self._run_async(transport))
        except RuntimeError:
            # If there's already an event loop (e.g., in some hosts), create a new one
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._run_async(transport))

