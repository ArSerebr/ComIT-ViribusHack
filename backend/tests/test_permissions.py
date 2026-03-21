"""can_edit_content / is_moderator_or_admin."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from app.core.permissions import can_edit_content, is_moderator_or_admin


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


def _user(role: str, uid: uuid.UUID) -> MagicMock:
    u = MagicMock()
    u.id = uid
    u.role = role
    return u


def test_owner_can_edit_own_content(user_id: uuid.UUID) -> None:
    u = _user("user", user_id)
    assert can_edit_content(u, user_id) is True


def test_user_cannot_edit_other_or_system(user_id: uuid.UUID) -> None:
    u = _user("user", user_id)
    assert can_edit_content(u, uuid.uuid4()) is False
    assert can_edit_content(u, None) is False


def test_moderator_can_edit_anything(user_id: uuid.UUID) -> None:
    u = _user("moderator", user_id)
    assert can_edit_content(u, None) is True
    assert can_edit_content(u, uuid.uuid4()) is True


def test_admin_can_edit_anything(user_id: uuid.UUID) -> None:
    u = _user("admin", user_id)
    assert can_edit_content(u, None) is True


def test_is_moderator_or_admin(user_id: uuid.UUID) -> None:
    assert is_moderator_or_admin(_user("user", user_id)) is False
    assert is_moderator_or_admin(_user("moderator", user_id)) is True
    assert is_moderator_or_admin(_user("admin", user_id)) is True
