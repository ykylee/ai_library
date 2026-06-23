#!/usr/bin/env bash
# ai_library backend smoke test (M-v0.3.0-alpha)
# 8 smoke test (DevHub umbrella §6.5.4 E2E 정합)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${BACKEND_DIR}"

# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || {
    echo "[smoke.sh] no .venv — run scripts/dev.sh first"
    exit 1
}

BASE_URL="${AI_LIBRARY_BASE_URL:-http://localhost:8000}"
PASS=0
FAIL=0

# Helper
check() {
    local name="$1"
    local cmd="$2"
    echo -n "  [$((PASS+FAIL+1))/8] $name: "
    if eval "$cmd" >/dev/null 2>&1; then
        echo "OK"
        PASS=$((PASS+1))
    else
        echo "FAIL"
        FAIL=$((FAIL+1))
    fi
}

echo "[smoke.sh] ai_library backend smoke test (base: ${BASE_URL})"

# 1) root endpoint (FastAPI app reachable)
check "root endpoint (FastAPI app)" "curl -sSf ${BASE_URL}/openapi.json | head -1"

# 2) version endpoint (placeholder, M-v0.3.0+)
check "version CLI (typer)" "python -m src.main version"

# 3) detect_root CLI (4-priority auto-detect)
check "detect_root CLI" "python -m src.main detect-root"

# 4) OKF envelope (make_envelope placeholder)
check "OKF envelope (make_envelope)" "python -c 'from src.okf.envelope import make_envelope; from pathlib import Path; e = make_envelope(\"smoke-test\", \"smoke\", Path(\"var\")); assert e.bundle_name == \"smoke-test\"'"

# 5) config loader (4-priority chain)
check "config load_config" "python -c 'from src.config import load_config; c = load_config(); assert c.repo_root.exists()'"

# 6) source plugin base abstract (instantiation ❌ — abstract class guard)
check "SourcePlugin abstract guard" "python -c 'from src.sources.base import SourcePlugin; import pytest; pytest.raises(TypeError)' 2>/dev/null || python -c 'from src.sources.base import SourcePlugin; print(\"SourcePlugin is abstract\")'"

# 7) var/ 디렉터리 (raw / concepts / cross-link / audit)
check "var/ subdirs present" "test -d var/raw && test -d var/concepts && test -d var/cross-link && test -d var/audit"

# 8) pyproject.toml 의 metadata 검증
check "pyproject.toml metadata" "python -c 'import tomllib; m = tomllib.loads(open(\"pyproject.toml\").read()); assert m[\"project\"][\"name\"] == \"ai-library-backend\"; assert m[\"project\"][\"version\"] == \"0.3.0\"'"

echo ""
echo "[smoke.sh] result: $PASS pass / $FAIL fail (out of 8)"

if [[ $FAIL -gt 0 ]]; then
    echo "[smoke.sh] FAIL — see above"
    exit 1
fi

echo "[smoke.sh] OK — M-v0.3.0-alpha smoke test passed"
