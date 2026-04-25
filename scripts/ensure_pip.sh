#!/usr/bin/env bash
# ensure_pip.sh - bootstrap pip for a selected Python interpreter
# Usage: bash ensure_pip.sh PYTHON PIP_COMMAND

set -u

PYTHON=${1:-python3}
PIP=${2:-"$PYTHON -m pip"}

echo "Ensuring pip is available for ${PYTHON}"

# Check if pip already available
if ${PYTHON} -m pip --version >/dev/null 2>&1; then
  echo "pip is already available for ${PYTHON}"
  exit 0
fi

# Try ensurepip
if ${PYTHON} -m ensurepip --upgrade >/dev/null 2>&1; then
  echo "Bootstrapped pip via ensurepip. Upgrading packaging tools..."
  ${PIP} install --upgrade pip setuptools wheel >/dev/null 2>&1 || true
  if ${PYTHON} -m pip --version >/dev/null 2>&1; then
    echo "pip is now available."
    exit 0
  fi
fi

echo "ensurepip failed or is unavailable; attempting platform package manager..."
OS=$(uname -s)
if [ "$OS" = "Linux" ]; then
  if command -v apt-get >/dev/null 2>&1; then
    echo "Attempting: sudo apt-get update && sudo apt-get install -y python3-pip"
    sudo apt-get update && sudo apt-get install -y python3-pip || true
  elif command -v yum >/dev/null 2>&1; then
    echo "Attempting: sudo yum install -y python3-pip"
    sudo yum install -y python3-pip || true
  else
    echo "No supported package manager found (apt-get/yum)."
  fi
elif [ "$OS" = "Darwin" ]; then
  if command -v brew >/dev/null 2>&1; then
    echo "Attempting: brew install python"
    brew install python || true
  else
    echo "Homebrew not found. Please install Homebrew or pip manually."
  fi
else
  echo "Unknown OS ($OS). Please install pip for ${PYTHON} manually."
fi

# Try get-pip.py as a last resort
echo "Attempting to bootstrap pip via get-pip.py (PyPA) as a last resort..."
TMP_GET=/tmp/get-pip.py
if command -v curl >/dev/null 2>&1; then
  curl -sS https://bootstrap.pypa.io/get-pip.py -o "$TMP_GET" || true
elif command -v wget >/dev/null 2>&1; then
  wget -q -O "$TMP_GET" https://bootstrap.pypa.io/get-pip.py || true
fi
if [ -f "$TMP_GET" ]; then
  ${PYTHON} "$TMP_GET" --disable-pip-version-check || true
fi

# Final check
if ${PYTHON} -m pip --version >/dev/null 2>&1; then
  echo "pip is now available."
  exit 0
fi

echo "Failed to install pip automatically. Please follow the project's README 'Setup' instructions." >&2
exit 1

