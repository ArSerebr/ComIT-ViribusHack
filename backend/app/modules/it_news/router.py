"""API внешних IT-новостей (RSS)."""

from __future__ import annotations

from uuid import UUID

from app.modules.it_news.deps import get_it_news_repository
from app.modules.it_news.models import ItNewsItem
from app.modules.it_news.repository import ItNewsRepository
from app.modules.it_news.schemas import ItNewsItemOut
from fastapi import APIRouter, Depends, HTTPException, Query

router = APIRouter(prefix="/api/it-news", tags=["it-news"])


def _to_out(row: ItNewsItem) -> ItNewsItemOut:
    return ItNewsItemOut(
        id=row.id,
        source=row.source,
        title=row.title,
        summary=row.summary,
        url=row.url,
        published_at=row.published_at,
    )


@router.get("", response_model=list[ItNewsItemOut])
async def list_it_news(
    repo: ItNewsRepository = Depends(get_it_news_repository),
    source: str | None = Query(None, description="habr, vc_ru, ixbt"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[ItNewsItemOut]:
    """Список новостей, собранных с RSS."""
    rows = await repo.list_recent(source=source, limit=limit, offset=offset)
    return [_to_out(r) for r in rows]


@router.get("/{item_id}", response_model=ItNewsItemOut)
async def get_it_news_item(
    item_id: UUID,
    repo: ItNewsRepository = Depends(get_it_news_repository),
) -> ItNewsItemOut:
    row = await repo.get_by_id(item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="News item not found")
    return _to_out(row)
