"""ai_library backend — FastAPI app entry + CLI.

본 파일은 M-v0.0.2-a foundation + 6 router 등록 진입점.

구조:
- typer CLI: `serve` / `version` / `detect-root`
- `create_app()` : FastAPI app factory + envelope middleware + 6 router 등록
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import typer
import uvicorn
from fastapi import FastAPI

from . import __version__
from .api import install_middleware, install_root_routers
from .api.v1 import api_v1_router
from .config import detect_repo_root, load_config

logger = logging.getLogger("ai_library")
cli = typer.Typer(help="ai_library backend CLI")


def create_app() -> FastAPI:
    """FastAPI app factory — M-v0.0.2-a foundation.

    등록 순서:
    1. envelope middleware (request.state.envelope 주입)
    2. error handler (ApiError → JSONResponse)
    3. /api/v1/ router aggregator (M-v0.0.2-a: health, M-v0.0.2-b: ingest/bundles, M-v0.0.2-c: concepts/raw/audit/graph)
    """
    app = FastAPI(
        title="ai_library backend",
        version=__version__,
        description="AI Agent Library — OKF bundle engine + LLM enrich agents.",
    )
    install_middleware(app)
    install_root_routers(app)
    app.include_router(api_v1_router)
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