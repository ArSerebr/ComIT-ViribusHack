"""ProfileService: моки репозитория и каталога интересов."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.modules.profile.models import UserProfile
from app.modules.profile.service import ProfileService
from fastapi import HTTPException
from schemas import ProfileMePatch


@pytest.mark.asyncio
async def test_get_me_commits_when_profile_created():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    uid = uuid.uuid4()
    profile = MagicMock(spec=UserProfile)
    profile.display_name = None
    profile.bio = None
    repo.get_or_create_profile = AsyncMock(return_value=(profile, True))
    repo.list_interest_ids = AsyncMock(return_value=[])
    catalog.labels_for_interest_ids = AsyncMock(return_value={})

    svc = ProfileService(session, repo, catalog)
    me = await svc.get_me(uid)

    session.commit.assert_awaited_once()
    assert me.displayName is None
    assert me.interests == []


@pytest.mark.asyncio
async def test_get_me_no_commit_when_exists():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    uid = uuid.uuid4()
    profile = MagicMock(spec=UserProfile)
    profile.display_name = "N"
    profile.bio = None
    repo.get_or_create_profile = AsyncMock(return_value=(profile, False))
    repo.list_interest_ids = AsyncMock(return_value=["i1"])
    catalog.labels_for_interest_ids = AsyncMock(return_value={"i1": "L1"})

    svc = ProfileService(session, repo, catalog)
    me = await svc.get_me(uid)

    session.commit.assert_not_awaited()
    assert len(me.interests) == 1
    assert me.interests[0].id == "i1"


@pytest.mark.asyncio
async def test_patch_me_validates_interests():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    uid = uuid.uuid4()
    profile = MagicMock(spec=UserProfile)
    repo.get_or_create_profile = AsyncMock(return_value=(profile, False))
    catalog.all_interest_option_ids_exist = AsyncMock(return_value=False)

    svc = ProfileService(session, repo, catalog)
    with pytest.raises(HTTPException) as ei:
        await svc.patch_me(uid, ProfileMePatch(interestIds=["bad"]))
    assert ei.value.status_code == 400


@pytest.mark.asyncio
async def test_patch_me_updates_and_commits():
    session = AsyncMock()
    repo = AsyncMock()
    catalog = AsyncMock()
    uid = uuid.uuid4()
    profile = MagicMock(spec=UserProfile)
    profile.display_name = None
    profile.bio = None
    repo.get_or_create_profile = AsyncMock(return_value=(profile, False))
    catalog.all_interest_option_ids_exist = AsyncMock(return_value=True)
    repo.replace_interests = AsyncMock()
    repo.list_interest_ids = AsyncMock(return_value=["a"])
    catalog.labels_for_interest_ids = AsyncMock(return_value={"a": "A"})

    svc = ProfileService(session, repo, catalog)
    await svc.patch_me(uid, ProfileMePatch(displayName="X", interestIds=["a"]))

    assert profile.display_name == "X"
    repo.replace_interests.assert_awaited_once_with(uid, ["a"])
    session.commit.assert_awaited()
