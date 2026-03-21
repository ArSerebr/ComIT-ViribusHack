"""Запись актуального OpenAPI в YAML при старте приложения."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import yaml
from fastapi import FastAPI

logger = logging.getLogger(__name__)


def _resolve_openapi_yaml_path() -> Path:
    """Путь к openapi.yaml: монорепо (../openapi) или только backend (/app/openapi)."""
    explicit = os.environ.get("OPENAPI_YAML_PATH", "").strip()
    if explicit:
        return Path(explicit).expanduser().resolve()

    app_dir = Path(__file__).resolve().parent
    backend_root = app_dir.parent
    repo_root = backend_root.parent
    monorepo_dir = repo_root / "openapi"
    if monorepo_dir.is_dir():
        return monorepo_dir / "openapi.yaml"
    return backend_root / "openapi" / "openapi.yaml"


def export_openapi_yaml(app: FastAPI) -> None:
    if os.environ.get("SKIP_OPENAPI_EXPORT", "").strip().lower() in ("1", "true", "yes"):
        return
    # Не трогаем файл при pytest / TestClient, чтобы CI и диффы были стабильны.
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return

    path = _resolve_openapi_yaml_path()
    try:
        spec = app.openapi()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(
                spec,
                f,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=120,
            )
    except OSError as e:
        logger.warning("OpenAPI export skipped: cannot write %s (%s)", path, e)
