"""Static seed fixtures (aligned with frontend data; no chat/AI).

API-facing shapes come from :mod:`schemas`; this module is the single source for seed rows.
"""

from __future__ import annotations

from typing import Any

from schemas import (
    ArticleTag,
    DashboardHome,
    DashboardHomeCourse,
    DashboardHomeEvents,
    DashboardHomeProductivity,
    FeaturedNewsItem,
    HubProject,
    IntegrationItem,
    InterestOption,
    LibraryArticle,
    LibraryBundle,
    LibraryHero,
    LibraryShowcaseItem,
    NewsMiniItem,
    NotificationItem,
    ParticipantRow,
    PersonPreview,
    ProductivityBlock,
    ProgressBlock,
    ProjectColumn,
    ProjectDetails,
    RecommendationCard,
    TodoBlock,
)

AV = "/img/avatar-photo.jpg"

__all__ = [
    "AV",
    "DASHBOARD_HOME",
    "FEATURED_NEWS",
    "KNOWN_PROJECT_IDS",
    "LIBRARY_BUNDLE",
    "NEWS_MINI",
    "NOTIFICATIONS",
    "PROJECT_DETAILS_BY_ID",
    "PROJECT_HUB_COLUMNS",
    "RECOMMENDATIONS",
]


def _hub_project(raw: dict[str, Any]) -> HubProject:
    pid = raw["id"]
    return HubProject(
        id=pid,
        code=raw["code"],
        title=raw["title"],
        description=raw["description"],
        teamName=raw["teamName"],
        updatedLabel=raw["updatedLabel"],
        teamAvatarUrl=raw.get("teamAvatarUrl") or AV,
        detailsUrl=raw.get("detailsUrl") or f"/projects/{pid}",
        visibility=raw.get("visibility"),
        isHot=raw.get("isHot"),
    )


def _column(col: dict[str, Any]) -> ProjectColumn:
    projects = [_hub_project(p) for p in col["projects"]]
    return ProjectColumn(
        id=col["id"],
        title=col["title"],
        count=len(projects),
        projects=projects,
    )


_RAW_HUB = [
    {
        "id": "idea",
        "title": "На стадии идеи",
        "projects": [
            {
                "id": "api-food-delivery",
                "code": "#TF9876",
                "visibility": "public",
                "title": "API для доставки еды",
                "isHot": True,
                "description": "Мы с командой разрабатываем систему для доставки еды, пока нам нужен UX/UI дизайнер",
                "teamName": "Frontend PRO",
                "updatedLabel": "3 дня назад",
            },
            {
                "id": "odyssey-ai",
                "code": "#TF9217",
                "visibility": "public",
                "title": "ODYSSEY AI",
                "description": "Хотим сделать AI для создания качественных презентаций и быстрого сторителлинга",
                "teamName": "Frontend PRO",
                "updatedLabel": "5 дней назад",
            },
            {
                "id": "campus-event-hub",
                "code": "#TF9012",
                "visibility": "public",
                "title": "Campus Event Hub",
                "description": "Платформа для организации университетских ивентов с ролями, слотами и заявками",
                "teamName": "IdeaSprint",
                "updatedLabel": "1 неделю назад",
            },
        ],
    },
    {
        "id": "development",
        "title": "В разработке",
        "projects": [
            {
                "id": "microservice-architecture",
                "code": "#EK9764",
                "visibility": "private",
                "title": "Архитектура для микросервиса",
                "description": "Мы с командой разрабатываем систему для доставки еды, пока нам нужен UX/UI дизайнер",
                "teamName": "GOMAKSTEAM",
                "updatedLabel": "1 месяц назад",
            },
            {
                "id": "study-sync",
                "code": "#EK9811",
                "visibility": "private",
                "title": "StudySync",
                "description": "Собираем единое рабочее пространство для учебных команд с задачами и файлами",
                "teamName": "GOMAKSTEAM",
                "updatedLabel": "2 недели назад",
            },
            {
                "id": "ml-notes-api",
                "code": "#EK9450",
                "visibility": "private",
                "title": "ML Notes API",
                "description": "Строим API и пайплайн для персональных конспектов по курсам и AI-поиска по ним",
                "teamName": "Core Unit",
                "updatedLabel": "6 дней назад",
            },
            {
                "id": "hack-ai-studio",
                "code": "#EK9635",
                "visibility": "private",
                "title": "Hack AI Studio",
                "description": "Делаем конструктор прототипов для хакатонов с шаблонами фич и аналитикой",
                "teamName": "MVP Crew",
                "updatedLabel": "9 дней назад",
            },
        ],
    },
    {
        "id": "integrated",
        "title": "Интегрированные",
        "projects": [
            {
                "id": "sensitive-llm",
                "code": "#KN2314",
                "title": "Sensitive LLM",
                "description": "Мы с командой разрабатываем систему для доставки еды, пока нам нужен UX/UI дизайнер",
                "teamName": "AI_dev_team32",
                "updatedLabel": "2 месяца назад",
            },
            {
                "id": "edugramm",
                "code": "#KN2482",
                "title": "EdugraMM",
                "isHot": True,
                "description": "Мы с командой разрабатываем систему для доставки еды, пока нам нужен UX/UI дизайнер",
                "teamName": "AI_dev_team32",
                "updatedLabel": "2 месяца назад",
            },
            {
                "id": "mentors-match",
                "code": "#KN2674",
                "title": "Mentors Match",
                "description": "Сервис рекомендаций для подбора менторов и проектных команд внутри вуза",
                "teamName": "Campus Core",
                "updatedLabel": "3 месяца назад",
            },
            {
                "id": "dev-portfolio-loop",
                "code": "#KN2539",
                "title": "Dev Portfolio Loop",
                "description": "Автоматизируем сбор артефактов по проекту и упаковку их в живое портфолио",
                "teamName": "Portfolio Lab",
                "updatedLabel": "3 месяца назад",
            },
            {
                "id": "startup-radar",
                "code": "#KN2781",
                "title": "Startup Radar",
                "description": "Лента университетских стартапов с витриной метрик, статусов и командного состава",
                "teamName": "Launch Team",
                "updatedLabel": "4 месяца назад",
            },
        ],
    },
]

PROJECT_HUB_COLUMNS: list[ProjectColumn] = [_column(c) for c in _RAW_HUB]

KNOWN_PROJECT_IDS: set[str] = {p.id for col in PROJECT_HUB_COLUMNS for p in col.projects}

NEWS_MINI: list[NewsMiniItem] = [
    NewsMiniItem(
        id="yandex-frontend-meetup",
        title="Недавно Яндекс провел митап по фронтенду, а также бесплатные вебинары по JavaScript и TypeScript",
        imageUrl="/img/news-photo.jpg",
        detailsUrl="/news/yandex-frontend-meetup",
    ),
    NewsMiniItem(
        id="hse-startup-cup",
        title="Недавно ВШЭ провел конкурс стартапов среди студентов и сотрудников университета",
        imageUrl="/img/poster-hackathon.jpg",
        detailsUrl="/news/hse-startup-cup",
    ),
    NewsMiniItem(
        id="ds-academy-open",
        title="В Центральном университете открыли академию Data Science",
        imageUrl="/img/poster-tech-conf.jpg",
        detailsUrl="/news/ds-academy-open",
    ),
    NewsMiniItem(
        id="neuroscale-launch",
        title="NeuroScale представил новый курс по разработке ИИ-сервисов на Yandex Cloud",
        imageUrl="/img/poster-web3.jpg",
        detailsUrl="/news/neuroscale-launch",
    ),
]

FEATURED_NEWS: list[FeaturedNewsItem] = [
    FeaturedNewsItem(
        id="students-ideathon",
        title="Идеатон для студентов",
        subtitle="Высшая школа экономики",
        description=(
            "В рамках идеатона участникам двух треков предстоит разработать концепт продукта и презентацию, "
            "применив навыки работы в команде, умение анализировать конкурентов и способность находить нестандартные решения."
        ),
        imageUrl="/img/poster-tech-talk.jpg",
        ctaLabel="Участвовать",
        detailsUrl="/events/students-ideathon",
    ),
    FeaturedNewsItem(
        id="sber-hackathon",
        title="Хакатон от Сбера",
        subtitle="Высшая школа экономики x SBER",
        description=(
            "Участникам хакатона нужно собрать MVP за 48 часов, подготовить демо и защитить решение перед жюри из индустрии."
        ),
        imageUrl="/img/poster-tech-conf.jpg",
        ctaLabel="Участвовать",
        detailsUrl="/events/sber-hackathon",
    ),
]

PROJECT_DETAILS_BY_ID: dict[str, ProjectDetails] = {
    "api-food-delivery": ProjectDetails(
        id="api-food-delivery",
        code="#TF9876",
        title="API для доставки еды",
        ownerName="Frontend Pro",
        detailsUrl="/projects/api-food-delivery",
        joinLabel="Присоединиться в команду",
        teamCaption="Все участники проекта",
        productivityCaption="Статистика за последний месяц",
        progressCaption="Какая часть уже готова",
        todoCaption="Последние задачи в проекте",
        integrationCaption="Подключайте сервисы для комфортной работы в команде",
        teamMembersPreview=[
            PersonPreview(id="maksdev", name="maksDEV", avatarUrl=AV, avatarVariant="default"),
            PersonPreview(id="backend-lead", name="daniil", avatarUrl=AV, avatarVariant="warm"),
            PersonPreview(id="ux-designer", name="liza", avatarUrl=AV, avatarVariant="cool"),
        ],
        productivity=ProductivityBlock(value="80%", delta="+15% за месяц"),
        progress=ProgressBlock(value="40%", percent=40),
        todo=TodoBlock(task="Завершить расчёт LTV, ARPU и CAC", updatedLabel="2 часа назад"),
        integrations=[
            IntegrationItem(
                id="github",
                brand="github",
                description="Автоматический деплой кода",
                statusLabel="Подключено",
                connectedSince="с 17.02.2026",
            ),
            IntegrationItem(
                id="timeweb",
                brand="timeweb",
                description="Хостинг ваших проектов",
                statusLabel="Подключено",
                connectedSince="с 31.01.2026",
            ),
        ],
        participants=[
            ParticipantRow(
                id="maksdev-row",
                name="maksDEV",
                avatarUrl=AV,
                avatarVariant="default",
                comitId="#78654",
                timeInProject="255 мин",
                role="Backend-разработчик",
                status="Работает",
                lastTask="Настройка ORM",
            ),
            ParticipantRow(
                id="daniil-row",
                name="daniilUI",
                avatarUrl=AV,
                avatarVariant="warm",
                comitId="#56342",
                timeInProject="193 мин",
                role="UX/UI дизайнер",
                status="Работает",
                lastTask="Доработка wireframes",
            ),
            ParticipantRow(
                id="liza-row",
                name="lizaQA",
                avatarUrl=AV,
                avatarVariant="cool",
                comitId="#90187",
                timeInProject="148 мин",
                role="QA-инженер",
                status="Работает",
                lastTask="Проверка сценариев заказа",
            ),
        ],
    )
}

LIBRARY_BUNDLE = LibraryBundle(
    showcaseItems=[
        LibraryShowcaseItem(
            id="netology-ml-engineer",
            brandLabel="нетология",
            eyebrow="Профессия",
            title="ML-инженер",
            imageUrl="/img/poster-120-1.jpg",
            hero=LibraryHero(
                id="ml-engineer-course",
                title="Курс «ML-инженер»",
                updatedLabel="3 дня назад",
                providerLabel="Яндекс практикум",
                description=(
                    "За 12 месяцев освоите востребованную профессию и получите реальный опыт: пройдёте полный цикл "
                    "ML-проекта — от подготовки данных и обучения моделей до внедрения и поддержки"
                ),
            ),
        ),
        LibraryShowcaseItem(
            id="practicum-mlops",
            brandLabel="Яндекс практикум",
            eyebrow="Интенсив",
            title="MLOps и продакшн",
            imageUrl="/img/poster-tech-talk.jpg",
            hero=LibraryHero(
                id="practicum-mlops-hero",
                title="Интенсив «MLOps и продакшн»",
                updatedLabel="6 дней назад",
                providerLabel="Яндекс практикум",
                description=(
                    "Разберёте жизненный цикл ML-сервисов в продакшне: деплой моделей, мониторинг качества, "
                    "автоматизацию пайплайнов и работу с инфраструктурой команды"
                ),
            ),
        ),
        LibraryShowcaseItem(
            id="skillbox-data-analyst",
            brandLabel="Skillbox",
            eyebrow="Профессия",
            title="Data Analyst",
            imageUrl="/img/poster-tech-conf.jpg",
            hero=LibraryHero(
                id="skillbox-da-hero",
                title="Профессия «Data Analyst»",
                updatedLabel="1 день назад",
                providerLabel="Skillbox",
                description=(
                    "Поймёте, как собирать и интерпретировать данные, строить отчёты и дашборды, формулировать выводы "
                    "для продукта и принимать решения на основе аналитики"
                ),
            ),
        ),
    ],
    interestOptions=[
        InterestOption(id="ml-engineering", label="ML инженеринг", selected=True),
        InterestOption(id="ux-ui", label="UX/UI дизайн", selected=False),
        InterestOption(id="frontend", label="Frontend stack", selected=False),
        InterestOption(id="backend", label="Backend stack", selected=False),
        InterestOption(id="testing", label="#Тестировка", selected=False),
        InterestOption(id="qa-courses", label="#QA курсы", selected=False),
    ],
    articles=[
        LibraryArticle(
            id="go-python-fullstack",
            tags=[
                ArticleTag(id="python", label="#Python", tone="green"),
                ArticleTag(id="golang", label="#GoLang", tone="cyan"),
                ArticleTag(id="fullstack", label="#FullStack", tone="coral"),
            ],
            title="Fullstack проект на Go и python",
            description=(
                "По ходу статьи эксперты рассказывают про типичные инженерные вещи — тестирование, прикладную "
                "бизнес-логику и интеграцию компонентов."
            ),
            authorName="PythonGo PRO",
            authorAvatarUrl=AV,
        ),
        LibraryArticle(
            id="catboost-xgboost-trees",
            tags=[
                ArticleTag(id="python", label="#Python", tone="green"),
                ArticleTag(id="ml", label="#ML", tone="yellow"),
            ],
            title="CatBoost, XGBoost + деревья",
            description=(
                "Данный обзор охватывает сразу несколько тем. Мы начнём с устройства решающего дерева и градиентного "
                "бустинга, затем подробно поговорим об XGBoost и CatBoost."
            ),
            authorName="Top MLman",
            authorAvatarUrl=AV,
        ),
        LibraryArticle(
            id="neural-generation-comparison",
            tags=[
                ArticleTag(id="python", label="#Python", tone="green"),
                ArticleTag(id="ai", label="#AI", tone="pink"),
                ArticleTag(id="gen-model", label="#generation model", tone="blue"),
            ],
            title="Сравнение нейросетей в генерациях",
            description=(
                "По ходу статьи эксперты рассказывают про типичные инженерные вещи — тестирование, прикладную "
                "бизнес-логику и интеграцию компонентов."
            ),
            authorName="MaxabouAI",
            authorAvatarUrl=AV,
        ),
    ],
)

NOTIFICATIONS: list[NotificationItem] = [
    NotificationItem(
        id="project-invite",
        type="invite",
        title="Вас взяли в проект API для доставки еды",
        unread=True,
        authorLabel="By",
        authorName="Frontend Pro",
        dateLabel="21 марта, 18:44",
        dateCaption="Время",
        path="/projects/api-food-delivery",
    ),
    NotificationItem(
        id="frontend-article",
        type="article",
        title="Вышла новая статья на тему",
        accentText="#Frontend разработка",
        ctaLabel="Читать",
        dateLabel="21 марта, 16:21",
        dateCaption="Время",
        path="/library",
    ),
]

RECOMMENDATIONS: list[RecommendationCard] = [
    RecommendationCard(
        id="hackathon",
        title="Хакатон 2026",
        subtitle="Погружение в ML + Frontend",
        image="/img/poster-hackathon.jpg",
        link="https://example.com/hackathon",
    ),
    RecommendationCard(
        id="web3",
        title="Web3 Design",
        subtitle="Интенсив по продукту",
        image="/img/poster-web3.jpg",
        link="https://example.com/web3-design",
    ),
    RecommendationCard(
        id="tech-conf",
        title="Tech Conference",
        subtitle="Frontend engineering",
        image="/img/poster-tech-conf.jpg",
        link="https://example.com/tech-conference",
    ),
    RecommendationCard(
        id="tech-talk",
        title="Tech Talk",
        subtitle="Современный стек разработчика",
        image="/img/poster-tech-talk.jpg",
        link="https://example.com/tech-talk",
    ),
]

DASHBOARD_HOME = DashboardHome(
    events=DashboardHomeEvents(count=16, deltaLabel="+2 за месяц"),
    productivity=DashboardHomeProductivity(value="80%", deltaLabel="+60% за месяц"),
    highlightCourse=DashboardHomeCourse(
        title="Data Science + ML",
        imageUrl="/img/course-image.png",
        path="/courses/data-science-ml",
    ),
)
