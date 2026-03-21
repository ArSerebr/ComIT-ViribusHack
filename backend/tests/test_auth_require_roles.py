"""Проверка зависимости require_roles: 403 при недостаточной роли, успех при допустимой."""
from __future__ import annotations

from unittest.mock import MagicMock

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.modules.auth.deps import current_active_user, require_roles
from app.modules.auth.models import User, UserRole


def _make_app():
    app = FastAPI()

    @app.get("/admin", dependencies=[Depends(require_roles("admin"))])
    async def admin_only():
        return {"role": "admin"}

    @app.get("/staff", dependencies=[Depends(require_roles("moderator", "admin"))])
    async def staff():
        return {"ok": True}

    return app


def test_require_roles_allows_admin():
    app = _make_app()

    async def user_admin():
        u = MagicMock(spec=User)
        u.role = UserRole.admin
        return u

    app.dependency_overrides[current_active_user] = user_admin
    with TestClient(app) as client:
        r = client.get("/admin")
    assert r.status_code == 200
    assert r.json() == {"role": "admin"}


def test_require_roles_forbidden_for_user_on_admin_route():
    app = _make_app()

    async def user_plain():
        u = MagicMock(spec=User)
        u.role = UserRole.user
        return u

    app.dependency_overrides[current_active_user] = user_plain
    with TestClient(app) as client:
        r = client.get("/admin")
    assert r.status_code == 403
    assert r.json()["detail"] == "Forbidden"


def test_require_roles_accepts_moderator_for_staff_route():
    app = _make_app()

    async def user_mod():
        u = MagicMock(spec=User)
        u.role = UserRole.moderator
        return u

    app.dependency_overrides[current_active_user] = user_mod
    with TestClient(app) as client:
        r = client.get("/staff")
    assert r.status_code == 200
    assert r.json() == {"ok": True}
