#!/usr/bin/env bash
# ai_library backend smoke test (M-v0.0.2-c)
# 8 smoke test (standalone 운영 검증, 17 endpoint cover)
#
# auto-starts FastAPI dev server in background (if not running), runs checks, kills at end.
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
SERVER_PID=""

# Ensure var/ subdirs exist (M-v0.0.2-a init)
mkdir -p var/raw var/concepts var/cross-link var/audit

# Auto-start dev server if not running
if ! curl -sSf "${BASE_URL}/openapi.json" >/dev/null 2>&1; then
    echo "[smoke.sh] no server on ${BASE_URL} — starting dev server in background"
    python -m src.main serve --host 127.0.0.1 --port 8000 >/tmp/ai_library_smoke.log 2>&1 &
    SERVER_PID=$!
    # wait up to 10s for server to be ready
    for _ in $(seq 1 20); do
        sleep 0.5
        if curl -sSf "${BASE_URL}/openapi.json" >/dev/null 2>&1; then
            break
        fi
    done
fi

# cleanup: kill server we started
cleanup() {
    if [[ -n "${SERVER_PID}" ]]; then
        kill "${SERVER_PID}" 2>/dev/null || true
        wait "${SERVER_PID}" 2>/dev/null || true
    fi
}
trap cleanup EXIT

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

# 1) GET /health — public health endpoint returns envelope-wrapped data
check "GET /health envelope" "python ${SCRIPT_DIR}/smoke_health.py"

# 2) version CLI (typer)
check "version CLI (typer)" "python -m src.main version"

# 3) GET /api/v1/health/protected with Path Y header — caller-provided user context 검증
check "Path Y protected health" "python ${SCRIPT_DIR}/smoke_path_y.py"

# 4) GET /api/v1/search — concept 검색 (M-v0.0.2-c)
check "GET /api/v1/search" "python ${SCRIPT_DIR}/smoke_search.py"

# 5) raw list + delete cycle (M-v0.0.2-c)
check "raw list + delete cycle" "python ${SCRIPT_DIR}/smoke_raw_cycle.py"

# 6) audit + graph reindex cycle (M-v0.0.2-c)
check "audit + graph reindex" "python ${SCRIPT_DIR}/smoke_audit_graph.py"

# 7) var/ 디렉터리 (raw / concepts / cross-link / audit)
check "var/ subdirs present" "test -d var/raw && test -d var/concepts && test -d var/cross-link && test -d var/audit"

# 8) pyproject.toml 의 metadata 검증
check "pyproject.toml metadata" "python ${SCRIPT_DIR}/smoke_pyproject.py"

echo ""
echo "[smoke.sh] result: $PASS pass / $FAIL fail (out of 8)"

if [[ $FAIL -gt 0 ]]; then
    echo "[smoke.sh] FAIL — see above"
    exit 1
fi

echo "[smoke.sh] OK — M-v0.0.2-c smoke test passed (17 endpoint cover)"