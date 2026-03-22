"""API хакатонов — read-only."""

from __future__ import annotations

from uuid import UUID

from app.modules.hackathons.deps import get_hackathon_repository
from app.modules.hackathons.models import Hackathon
from app.modules.hackathons.repository import HackathonRepository
from app.modules.hackathons.schemas import HackathonDetail, HackathonItem
from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter(prefix="/api/hackathons", tags=["hackathons"])


def _to_item(h: Hackathon) -> HackathonItem:
    return HackathonItem(
        id=h.id,
        external_id=h.external_id,
        source=h.source,
        title=h.title,
        description=h.description,
        start_date=h.start_date,
        end_date=h.end_date,
        location=h.location,
        is_online=h.is_online,
        prize_pool=h.prize_pool,
        url=h.url,
        image_url=h.image_url,
        organizer=h.organizer,
        tags=h.tags,
        status=h.status,
    )


def _to_detail(h: Hackathon) -> HackathonDetail:
    return HackathonDetail(
        id=h.id,
        external_id=h.external_id,
        source=h.source,
        title=h.title,
        description=h.description,
        description_raw=h.description_raw,
        start_date=h.start_date,
        end_date=h.end_date,
        registration_deadline=h.registration_deadline,
        location=h.location,
        is_online=h.is_online,
        prize_pool=h.prize_pool,
        url=h.url,
        image_url=h.image_url,
        organizer=h.organizer,
        tags=h.tags,
        status=h.status,
    )


@router.get("", response_model=list[HackathonItem])
async def list_hackathons(
    repo: HackathonRepository = Depends(get_hackathon_repository),
    source: str | None = Query(None, description="Фильтр по источнику"),
    status: str | None = Query(None, description="Фильтр по статусу"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[HackathonItem]:
    """Список хакатонов (парсятся с hacklist.ru, cups.online и др.)."""
    rows = await repo.list_all(source=source, status=status, limit=limit, offset=offset)
    return [_to_item(r) for r in rows]


@router.get("/{hackathon_id}", response_model=HackathonDetail)
async def get_hackathon(
    hackathon_id: UUID,
    repo: HackathonRepository = Depends(get_hackathon_repository),
) -> HackathonDetail:
    """Детали хакатона (включая сырое описание для ML)."""
    row = await repo.get_by_id(hackathon_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Hackathon not found")
    return _to_detail(row)
