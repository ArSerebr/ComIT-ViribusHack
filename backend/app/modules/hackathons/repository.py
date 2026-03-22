"""Репозиторий хакатонов."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hackathons.models import Hackathon
from app.modules.hackathons.upcoming import hackathon_is_upcoming


class HackathonRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(
        self,
        *,
        source: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        only_upcoming: bool = False,
    ) -> list[Hackathon]:
        if only_upcoming:
            q = select(Hackathon).order_by(Hackathon.start_date.asc().nullslast())
        else:
            q = select(Hackathon).order_by(Hackathon.start_date.desc().nullslast())
        if source:
            q = q.where(Hackathon.source == source)
        if status:
            q = q.where(Hackathon.status == status)
        if only_upcoming:
            cap = min(max((offset + limit) * 25, limit * 25), 2000)
            q = q.limit(cap)
        else:
            q = q.limit(limit).offset(offset)
        result = await self._session.execute(q)
        rows = list(result.scalars().all())
        if only_upcoming:
            rows = [r for r in rows if hackathon_is_upcoming(r)]
            return rows[offset : offset + limit]
        return rows

    async def get_by_id(self, hackathon_id: uuid.UUID) -> Hackathon | None:
        result = await self._session.execute(
            select(Hackathon).where(Hackathon.id == hackathon_id)
        )
        return result.scalar_one_or_none()
