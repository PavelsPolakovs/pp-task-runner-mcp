import importlib
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple


def check_required_packages() -> None:
    """Verify a small set of runtime packages are importable.

    If any are missing, print a clear error listing the missing packages
    and copy-paste-ready install commands, then exit with a non-zero
    status to avoid running in a degraded/interactive-missing state.
    """
    # Map requirement token -> importable module name
    required: Dict[str, str] = {
        "prompt_toolkit": "prompt_toolkit",
        "python-dotenv": "dotenv",
    }

    missing: List[Tuple[str, str]] = []
    for req_token, module_name in required.items():
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append((req_token, module_name))

    if not missing:
        return

    print("\nERROR: Missing required packages for MCP.", file=sys.stderr)
    print("These packages are required. Please install them before using this MCP:\n", file=sys.stderr)
    for req_token, module_name in missing:
        print(f" - {req_token} (import as '{module_name}')", file=sys.stderr)

    repo_root = Path(__file__).resolve().parents[1]
    req_file = repo_root / "requirements.txt"
    readme_path = repo_root / "README.md"

    # Ready-to-copy pip command that installs the specific missing packages
    pkg_list = " ".join(req for req, _ in missing)
    pip_cmd = f"python3 -m pip install {pkg_list}"

    print("\nYou can install only the missing packages with this command:", file=sys.stderr)
    print(f"  {pip_cmd}", file=sys.stderr)
    print("\nOr install everything from the project's requirements file:", file=sys.stderr)
    print(f"  python3 -m pip install -r {req_file}", file=sys.stderr)
    print("Or use the Makefile helper:", file=sys.stderr)
    print("  make install-dev\n", file=sys.stderr)
    print(f"  If 'pip' is missing on your system, follow the README 'Setup' section to install Python/pip or use a virtualenv.", file=sys.stderr)
    print(f"  Link to README file {readme_path}", file=sys.stderr)
    sys.exit(2)

