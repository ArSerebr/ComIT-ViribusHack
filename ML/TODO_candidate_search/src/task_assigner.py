"""Shim: каноническая реализация в backend (app.modules.projects.task_assignment)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_BACKEND = _REPO_ROOT / "backend"
if _BACKEND.is_dir() and str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.modules.projects.task_assignment.task_assigner import (  # noqa: E402
    TaskAssignmentModel,
    create_embedding_provider,
    cosine_similarity,
    load_json,
    normalize_member,
    normalize_task_dict,
    textify_member,
    textify_task,
)

__all__ = [
    "TaskAssignmentModel",
    "create_embedding_provider",
    "cosine_similarity",
    "load_json",
    "normalize_member",
    "normalize_task_dict",
    "textify_member",
    "textify_task",
]
