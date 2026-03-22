"""PulseCore AI chat proxy router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.modules.auth.deps import current_active_user
from app.modules.auth.models import User
from app.modules.pulse.deps import get_pulse_service
from app.modules.pulse.service import PulseService

router = APIRouter(prefix="/api/pulse", tags=["pulse"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    task_id: str


@router.post("/chat", response_model=ChatResponse)
async def post_chat(
    body: ChatRequest,
    user: User = Depends(current_active_user),
    service: PulseService = Depends(get_pulse_service),
) -> ChatResponse:
    """Submit a message to PulseCore AI. Returns task_id for polling."""
    task_id = await service.submit_chat(user.id, body.message.strip())
    return ChatResponse(task_id=task_id)


@router.get("/task/{task_id}")
async def get_task(
    task_id: str,
    user: User = Depends(current_active_user),
    service: PulseService = Depends(get_pulse_service),
):
    """Poll task status. Returns {status, result?}."""
    return await service.poll_task(task_id)


@router.get("/status")
async def get_status(
    user: User = Depends(current_active_user),
    service: PulseService = Depends(get_pulse_service),
):
    """Get current AI processing status for the user."""
    return await service.get_status(user.id)


@router.get("/history")
async def get_history(
    user: User = Depends(current_active_user),
    service: PulseService = Depends(get_pulse_service),
):
    """Get chat history for the user."""
    return await service.get_history(user.id)


@router.post("/execute")
async def post_execute(
    user: User = Depends(current_active_user),
    service: PulseService = Depends(get_pulse_service),
):
    """Confirm execution of a pending task."""
    return await service.execute_task(user.id)


@router.post("/cancel")
async def post_cancel(
    user: User = Depends(current_active_user),
    service: PulseService = Depends(get_pulse_service),
):
    """Cancel a pending task."""
    return await service.cancel_task(user.id)
