"""Import all ORM modules so :class:`Base.metadata` is complete for Alembic."""

from __future__ import annotations

from app.modules.analytics import models as _analytics_models  # noqa: F401
from app.modules.auth import models as _auth_models  # noqa: F401
from app.modules.dashboard import models as _dashboard_models  # noqa: F401
from app.modules.library import models as _library_models  # noqa: F401
from app.modules.news import models as _news_models  # noqa: F401
from app.modules.notifications import models as _notifications_models  # noqa: F401
from app.modules.profile import models as _profile_models  # noqa: F401
from app.modules.projects import models as _projects_models  # noqa: F401
from app.modules.hackathons import models as _hackathons_models  # noqa: F401
