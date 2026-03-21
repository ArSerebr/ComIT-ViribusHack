"""ComIT Viribus API — Modular Monolith.

main.py is assembly only: creates FastAPI app, registers routers from modules.
No business logic, no DB access, no in-memory data. All data comes from PostgreSQL
via module layers: Router → Service → Repository → ORM.
"""

from __future__ import annotations

from app.core.observability import register_observability
from app.lifespan import lifespan
from app.modules.analytics import router as analytics_router
from app.modules.auth.router import router as auth_router
from app.modules.dashboard import router as dashboard_router
from app.modules.library import router as library_router
from app.modules.library.admin_router import router as library_admin_router
from app.modules.news import router as news_router
from app.modules.notifications import router as notifications_router
from app.modules.profile import router as profile_router
from app.modules.profile.admin_router import router as profile_admin_router
from app.modules.projects import router as projects_router
from app.modules.projects.admin_router import router as projects_admin_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Registry of module routers — main only assembles, no logic.
# Auth (fastapi-users): JWT /register /users under prefix `/api` (see app.modules.auth.router).
_MODULE_ROUTERS = [
    auth_router,
    analytics_router,
    news_router,
    projects_router,
    projects_admin_router,
    library_router,
    library_admin_router,
    profile_router,
    profile_admin_router,
    notifications_router,
    dashboard_router,
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="ComIT Viribus API",
        version="1.0.0",
        description="REST API для SPA (без эндпоинтов ИИ-чата)",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_parameters={"persistAuthorization": True},
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_observability(app)
    for router in _MODULE_ROUTERS:
        app.include_router(router)
    return app


app = create_app()
