"""4-priority REPO_ROOT auto-detect + config loader.

4-priority chain:
1. explicit `--repo-root` flag / `AI_LIBRARY_REPO_ROOT` env (1순위)
2. `git rev-parse --show-toplevel` (in-repo 운영 시 자동 detect)
3. legacy fallback: 부모 디렉터리 5단계 walk (AGENTS.md + web/ + backend/ 마커)
4. fallback: cwd (1회 stderr deprecation warning)
"""
from __future__ import annotations

import logging
import os
import subprocess
import warnings
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


def detect_repo_root(start: Path | None = None) -> Path:
    """4-priority REPO_ROOT auto-detect."""
    start = start or Path.cwd()

    # 1) env var (1순위)
    env_root = os.environ.get("AI_LIBRARY_REPO_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    # 2) git rev-parse --show-toplevel
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).resolve()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 3) legacy fallback: 부모 5단계 walk
    current = start.resolve()
    for _ in range(5):
        if (current / "AGENTS.md").exists() and (current / "web").exists() and (current / "backend").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    # 4) fallback: cwd + deprecation warning
    warnings.warn(
        f"ai_library: could not auto-detect REPO_ROOT from {start}; using cwd. "
        "Set AI_LIBRARY_REPO_ROOT env var or use --repo-root flag.",
        DeprecationWarning,
        stacklevel=2,
    )
    return start.resolve()


@dataclass(frozen=True)
class Config:
    """ai_library backend config (M-v0.3.0-alpha minimal)."""

    repo_root: Path
    var_dir: Path = field(default_factory=lambda: Path("./var"))
    storage_mode: str = "file"  # file | db (M-v0.3.2+ 부터 db 모드 활성화)
    log_level: str = "info"
    host: str = "0.0.0.0"
    port: int = 8000

    def __post_init__(self) -> None:
        # var_dir 가 relative 면 repo_root 기준
        if not self.var_dir.is_absolute():
            object.__setattr__(self, "var_dir", self.repo_root / "backend" / self.var_dir)


def load_config(repo_root: Path | None = None) -> Config:
    """Load config with env var + default fallback."""
    root = repo_root or detect_repo_root()
    return Config(
        repo_root=root,
        var_dir=Path(os.environ.get("AI_LIBRARY_VAR_DIR", "./var")),
        storage_mode=os.environ.get("AI_LIBRARY_STORAGE_MODE", "file"),
        log_level=os.environ.get("AI_LIBRARY_LOG_LEVEL", "info"),
        host=os.environ.get("AI_LIBRARY_HOST", "0.0.0.0"),
        port=int(os.environ.get("AI_LIBRARY_PORT", "8000")),
    )
