import asyncio
import inspect
from contextlib import asynccontextmanager
from typing import Callable, Any, Dict


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

        # For stdio transport, keep running until EOF on stdin or short timeout
        if transport == "stdio":
            print("[FastMCP shim] (stdio) waiting briefly to simulate server...")
            # wait briefly to simulate runtime
            await asyncio.sleep(1)
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

