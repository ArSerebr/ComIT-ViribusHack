"""Логика отбора предстоящих хакатонов."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from app.modules.hackathons.models import Hackathon
from app.modules.hackathons.upcoming import hackathon_is_upcoming


def _row(**kwargs) -> Hackathon:
    base = dict(
        id=uuid4(),
        external_id="x",
        source="test",
        title="T",
        start_date=None,
        end_date=None,
        status="upcoming",
    )
    base.update(kwargs)
    return Hackathon(**base)


def test_date_only_start_tomorrow_visible() -> None:
    t = date.today() + timedelta(days=1)
    h = _row(start_date=t.isoformat())
    assert hackathon_is_upcoming(h)


def test_date_only_start_yesterday_hidden() -> None:
    t = date.today() - timedelta(days=1)
    h = _row(start_date=t.isoformat())
    assert not hackathon_is_upcoming(h)


def test_end_datetime_future_visible() -> None:
    now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
    end = datetime(2026, 6, 20, 18, 0, tzinfo=timezone.utc)
    h = _row(start_date="2026-06-10T10:00:00+00:00", end_date=end.isoformat())
    assert hackathon_is_upcoming(h, now=now)


def test_end_datetime_past_hidden() -> None:
    now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
    h = _row(start_date="2026-06-01T10:00:00+00:00", end_date="2026-06-10T18:00:00+00:00")
    assert not hackathon_is_upcoming(h, now=now)


def test_russian_date_from_parser_visible() -> None:
    """Как в hacklist/networkly: «22 марта 2026»."""
    now = datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc)
    h = _row(start_date="22 марта 2026")
    assert hackathon_is_upcoming(h, now=now)


def test_russian_date_in_longer_string() -> None:
    now = datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc)
    h = _row(start_date="12 - 22 марта 2026")
    assert hackathon_is_upcoming(h, now=now)
