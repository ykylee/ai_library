"""ai_library backend — FastAPI app entry + CLI.

본 파일은 M-v0.3.0-alpha placeholder.
M-v0.3.0+ 부터 FastAPI app + typer CLI + 4-priority REPO_ROOT auto-detect + API versioning 라우터 등록.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import typer
import uvicorn
from fastapi import FastAPI

from . import __version__
from .config import detect_repo_root, load_config
from .okf import make_envelope, parse_envelope  # noqa: F401  (M-v0.3.0+ register)

logger = logging.getLogger("ai_library")
cli = typer.Typer(help="ai_library backend CLI (M-v0.3.0-alpha)")


def create_app() -> FastAPI:
    """FastAPI app factory.

    M-v0.3.0+ 부터 src.api.v0_2 의 6 router (ingest / bundles / concepts / raw / audit / graph) 등록.
    M-v0.3.2+ 부터 /api/v0-3/ 라우터 추가 (deprecation policy §16.2 정합).
    """
    app = FastAPI(
        title="ai_library backend",
        version=__version__,
        description="AI Agent Library — OKF bundle engine + LLM enrich agents. 1차 출처: DevHub v0.2.0 backend-knowledge (2026-06-23 extraction).",
    )
    # M-v0.3.0+ router 등록 자리
    # from .api.v0_2 import ingest, bundles, concepts, raw, audit, graph
    # app.include_router(ingest.router, prefix="/api/v0-2/ingest", tags=["ingest"])
    # ...
    return app


@cli.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", help="Bind host"),
    port: int = typer.Option(8000, "--port", help="Bind port"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on code change"),
    repo_root: Path | None = typer.Option(None, "--repo-root", help="Explicit repo root (4-priority auto-detect의 1순위)"),
) -> None:
    """Run FastAPI dev server (uvicorn)."""
    config = load_config(repo_root=repo_root)
    logger.info("ai_library v%s starting on %s:%d (repo_root=%s)", __version__, host, port, config.repo_root)
    uvicorn.run("src.main:create_app", host=host, port=port, reload=reload, factory=True)


@cli.command()
def version() -> None:
    """Print ai_library version."""
    typer.echo(f"ai_library v{__version__}")


@cli.command()
def detect_root() -> None:
    """Print detected REPO_ROOT (4-priority auto-detect 검증용)."""
    root = detect_repo_root()
    typer.echo(str(root))


def main() -> None:
    """Console script entry point (pyproject.toml [project.scripts])."""
    cli()


if __name__ == "__main__":
    sys.exit(main())
