"""HTTP: роутеры fastapi-users под префиксом `/api`."""

from __future__ import annotations

from app.modules.auth.deps import fastapi_users
from app.modules.auth.jwt_backend import auth_backend
from app.modules.auth.schemas import UserCreate, UserRead, UserUpdate
from fastapi import APIRouter

router = APIRouter(prefix="/api")

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
