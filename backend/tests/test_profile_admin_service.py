"""ProfileService admin CRUD for universities."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from app.modules.profile.schemas import UniversityCreateBody, UniversityUpdateBody
from app.modules.profile.service import ProfileService


@pytest.mark.asyncio
async def test_admin_create_university_ok():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    repo.get_university = AsyncMock(return_value=None)
    repo.create_university = AsyncMock()

    svc = ProfileService(session, repo, catalog)
    status, item = await svc.admin_create_university(
        UniversityCreateBody(id="msu", name="МГУ", sort_order=1)
    )

    assert status == "ok"
    assert item is not None
    assert item.id == "msu"
    assert item.name == "МГУ"
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_create_university_exists():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    repo.get_university = AsyncMock(return_value=object())  # exists

    svc = ProfileService(session, repo, catalog)
    status, item = await svc.admin_create_university(
        UniversityCreateBody(id="msu", name="МГУ")
    )

    assert status == "exists"
    assert item is None
    repo.create_university.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_update_university_ok():
    from app.modules.profile.models import ProfileUniversity
    from unittest.mock import MagicMock

    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    row = MagicMock(spec=ProfileUniversity)
    row.id = "msu"
    row.name = "МГУ им. Ломоносова"
    repo.update_university = AsyncMock(return_value=row)

    svc = ProfileService(session, repo, catalog)
    status, item = await svc.admin_update_university(
        "msu", UniversityUpdateBody(name="МГУ им. Ломоносова")
    )

    assert status == "ok"
    assert item is not None
    assert item.name == "МГУ им. Ломоносова"
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_update_university_not_found():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    repo.update_university = AsyncMock(return_value=None)

    svc = ProfileService(session, repo, catalog)
    status, item = await svc.admin_update_university(
        "unknown", UniversityUpdateBody(name="X")
    )

    assert status == "not_found"
    assert item is None


@pytest.mark.asyncio
async def test_admin_delete_university_ok():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    repo.get_university = AsyncMock(return_value=object())
    repo.count_profiles_with_university = AsyncMock(return_value=0)
    repo.delete_university = AsyncMock(return_value=True)

    svc = ProfileService(session, repo, catalog)
    st = await svc.admin_delete_university("msu")

    assert st == "ok"
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_delete_university_not_found():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    repo.get_university = AsyncMock(return_value=None)

    svc = ProfileService(session, repo, catalog)
    st = await svc.admin_delete_university("unknown")

    assert st == "not_found"
    repo.delete_university.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_delete_university_in_use():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    repo.get_university = AsyncMock(return_value=object())
    repo.count_profiles_with_university = AsyncMock(return_value=3)

    svc = ProfileService(session, repo, catalog)
    st = await svc.admin_delete_university("msu")

    assert st == "in_use"
    repo.delete_university.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_list_universities():
    from app.modules.profile.models import ProfileUniversity
    from unittest.mock import MagicMock

    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    r1 = MagicMock(spec=ProfileUniversity)
    r1.id = "msu"
    r1.name = "МГУ"
    r2 = MagicMock(spec=ProfileUniversity)
    r2.id = "hse"
    r2.name = "ВШЭ"
    repo.list_universities_ordered = AsyncMock(return_value=[r1, r2])

    svc = ProfileService(session, repo, catalog)
    items = await svc.admin_list_universities()

    assert len(items) == 2
    assert items[0].id == "msu" and items[0].name == "МГУ"
    assert items[1].id == "hse" and items[1].name == "ВШЭ"
