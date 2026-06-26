"""Smoke check #8: pyproject.toml 의 metadata 검증 (version = 0.0.1)."""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path


def main() -> int:
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with pyproject.open("rb") as f:
        m = tomllib.load(f)
    assert m["project"]["name"] == "ai-library-backend", f"name: {m['project']}"
    assert m["project"]["version"] == "0.0.1", f"version: {m['project']}"
    return 0


if __name__ == "__main__":
    sys.exit(main())