#!/usr/bin/env bash
# ai_library backend dev server (M-v0.3.0-alpha)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${BACKEND_DIR}"

# 1. venv 보장
if [[ ! -d ".venv" ]]; then
    echo "[dev.sh] creating venv (Python 3.13+)"
    python3.13 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# 2. editable install (이미 됐다면 skip)
if [[ ! -f ".venv/installed.marker" ]]; then
    echo "[dev.sh] pip install -e ."
    pip install --quiet --upgrade pip
    pip install --quiet -e ".[dev]"
    touch .venv/installed.marker
fi

# 3. detect repo root
REPO_ROOT="${AI_LIBRARY_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo "${BACKEND_DIR}/..")}"
export AI_LIBRARY_REPO_ROOT="$(cd "${REPO_ROOT}" && pwd)"

# 4. run uvicorn (FastAPI app)
HOST="${AI_LIBRARY_HOST:-0.0.0.0}"
PORT="${AI_LIBRARY_PORT:-8000}"
RELOAD="${AI_LIBRARY_RELOAD:-true}"

echo "[dev.sh] ai_library backend starting on http://${HOST}:${PORT}"
echo "[dev.sh] repo_root: ${AI_LIBRARY_REPO_ROOT}"
exec python -m uvicorn src.main:create_app --host "${HOST}" --port "${PORT}" --reload --factory
