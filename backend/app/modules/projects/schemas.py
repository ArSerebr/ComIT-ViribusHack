"""Projects module API schemas (request/response). Router uses these as adapters."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class JoinRequest(BaseModel):
    message: Optional[str] = None


class JoinResponse(BaseModel):
    ok: bool = True
    project_id: str
