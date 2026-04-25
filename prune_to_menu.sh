#!/usr/bin/env bash
set -euo pipefail

# Safe pruning script: remove all files in the repository except the
# minimal set required to run the menu. This script preserves a temporary
# copy while it removes other files, so the allowed files remain afterwards.
#
# IMPORTANT: This is a destructive operation. Run this only if you are
# certain. The script will prompt for confirmation.

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TS=$(date +%s)
PRESERVE_DIR="$REPO_ROOT/.preserve_menu_$TS"

ALLOW=(
  "src/menu_mcp_server.py"
  "src/main.py"
  "src/mcp/server/fastmcp.py"
  "src/mcp/server/__init__.py"
  "src/mcp/__init__.py"
  "requirements.txt"
  "prune_to_menu.sh"
)

echo "Repository root: $REPO_ROOT"
echo "This will remove all files and folders in the repository except the following allowlist:"
for p in "${ALLOW[@]}"; do
  echo "  - $p"
done

read -rp $'Type DELETE (in uppercase) to proceed: ' CONFIRM
if [[ "$CONFIRM" != "DELETE" ]]; then
  echo "Aborted by user. No changes made."
  exit 1
fi

echo "Creating preserve copy at: $PRESERVE_DIR"
mkdir -p "$PRESERVE_DIR"

for p in "${ALLOW[@]}"; do
  srcpath="$REPO_ROOT/$p"
  if [[ -e "$srcpath" ]]; then
    destdir="$PRESERVE_DIR/$(dirname "$p")"
    mkdir -p "$destdir"
    cp -a "$srcpath" "$destdir/"
  fi
done

echo "Removing everything except .git and preserve copy..."
shopt -s dotglob
for entry in "$REPO_ROOT"/*; do
  name=$(basename "$entry")
  if [[ "$name" == ".git" ]]; then
    echo "Skipping .git"
    continue
  fi
  if [[ "$entry" == "$PRESERVE_DIR" ]]; then
    echo "Skipping preserve dir"
    continue
  fi
  rm -rf "$entry"
done

echo "Restoring allowed files..."
cp -a "$PRESERVE_DIR"/* "$REPO_ROOT/" || true
rm -rf "$PRESERVE_DIR"

echo "Prune complete. The repository now contains only the allowlisted files (plus .git)."
echo "Run 'git status' to review changes, and commit or discard as needed."

exit 0

