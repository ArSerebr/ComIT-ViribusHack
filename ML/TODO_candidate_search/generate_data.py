import json
import random
import sys
from pathlib import Path


SEED = 42
PROJECTS_COUNT = 100


PRODUCT_TYPES = [
    {
        "name": "платформа для совместной учебы",
        "audience": "студентов вузов",
        "domain": "edtech",
        "features": ["чат-комнаты", "календарь дедлайнов", "совместные заметки"],
    },
    {
        "name": "сервис поиска стажировок",
        "audience": "junior-специалистов",
        "domain": "career",
        "features": ["умный поиск вакансий", "профиль кандидата", "трекер откликов"],
    },
    {
        "name": "маркетплейс студенческих услуг",
        "audience": "студентов и выпускников",
        "domain": "marketplace",
        "features": ["каталог услуг", "рейтинги исполнителей", "безопасные сделки"],
    },
    {
        "name": "приложение для мероприятий кампуса",
        "audience": "участников университетских сообществ",
        "domain": "community",
        "features": ["лента событий", "регистрация на мероприятия", "push-уведомления"],
    },
    {
        "name": "API для доставки еды",
        "audience": "студенческих команд и кафе",
        "domain": "foodtech",
        "features": ["каталог меню", "трекер заказов", "интеграции с платежами"],
    },
    {
        "name": "платформа карьерного менторства",
        "audience": "студентов старших курсов",
        "domain": "career",
        "features": ["матчинг с менторами", "видеовстречи", "карьерные планы"],
    },
    {
        "name": "трекер привычек и продуктивности",
        "audience": "студентов и молодых специалистов",
        "domain": "productivity",
        "features": ["дневные цели", "напоминания", "аналитика прогресса"],
    },
    {
        "name": "сервис обмена учебными материалами",
        "audience": "студентов технических специальностей",
        "domain": "edtech",
        "features": ["облачное хранилище", "теги материалов", "поиск по конспектам"],
    },
    {
        "name": "платформа волонтерских проектов",
        "audience": "активных студентов",
        "domain": "social",
        "features": ["поиск инициатив", "расписание смен", "учет часов волонтерства"],
    },
    {
        "name": "конструктор портфолио",
        "audience": "дизайнеров, разработчиков и аналитиков",
        "domain": "creator",
        "features": ["шаблоны страниц", "экспорт в PDF", "персональная аналитика"],
    },
]


TASK_BLUEPRINTS = {
    "discovery": [
        {
            "title": "Провести интервью с пользователями",
            "description": "Собрать боли, сценарии использования и критерии успеха продукта.",
            "skills": ["customer development", "research", "product discovery"],
            "category": "product",
        },
        {
            "title": "Сформировать roadmap MVP",
            "description": "Определить обязательные функции, ограничения релиза и приоритеты команды.",
            "skills": ["product management", "prioritization", "backlog management"],
            "category": "product",
        },
    ],
    "design": [
        {
            "title": "Подготовить user flow и wireframes",
            "description": "Спроектировать пользовательские сценарии и структуру ключевых экранов.",
            "skills": ["ux design", "figma", "information architecture"],
            "category": "design",
        },
        {
            "title": "Собрать UI-kit для MVP",
            "description": "Подготовить цветовую систему, компоненты и базовые паттерны интерфейса.",
            "skills": ["ui design", "figma", "design systems"],
            "category": "design",
        },
    ],
    "backend": [
        {
            "title": "Спроектировать схему базы данных",
            "description": "Определить сущности, связи, индексы и ограничения для доменной модели.",
            "skills": ["sql", "database design", "backend architecture"],
            "category": "backend",
        },
        {
            "title": "Реализовать REST API для основных сущностей",
            "description": "Создать эндпоинты CRUD, валидацию данных и обработку ошибок.",
            "skills": ["python", "fastapi", "api development"],
            "category": "backend",
        },
        {
            "title": "Настроить авторизацию и роли",
            "description": "Добавить регистрацию, логин, JWT-сессии и разграничение доступа.",
            "skills": ["authentication", "backend", "security"],
            "category": "backend",
        },
    ],
    "frontend": [
        {
            "title": "Реализовать пользовательский dashboard",
            "description": "Собрать экран с основными метриками, карточками и статусами задач.",
            "skills": ["react", "typescript", "frontend"],
            "category": "frontend",
        },
        {
            "title": "Подключить формы и валидацию",
            "description": "Сделать формы создания сущностей, проверку полей и обработку ошибок API.",
            "skills": ["react", "form validation", "frontend"],
            "category": "frontend",
        },
        {
            "title": "Интегрировать фронтенд с API",
            "description": "Подключить запросы, состояния загрузки, кеширование и обработку edge cases.",
            "skills": ["react", "api integration", "state management"],
            "category": "frontend",
        },
    ],
    "mobile": [
        {
            "title": "Собрать мобильный экран онбординга",
            "description": "Реализовать сценарий первого входа и сбора базовых настроек пользователя.",
            "skills": ["flutter", "mobile ui", "state management"],
            "category": "mobile",
        },
        {
            "title": "Настроить push-уведомления",
            "description": "Подключить мобильные уведомления по событиям продукта и действиям команды.",
            "skills": ["flutter", "firebase", "mobile"],
            "category": "mobile",
        },
    ],
    "devops": [
        {
            "title": "Настроить CI/CD пайплайн",
            "description": "Автоматизировать тесты, сборку и деплой приложения в staging.",
            "skills": ["devops", "github actions", "docker"],
            "category": "devops",
        },
        {
            "title": "Подготовить окружение и контейнеризацию",
            "description": "Собрать docker-конфигурацию, переменные окружения и локальный запуск.",
            "skills": ["docker", "linux", "deployment"],
            "category": "devops",
        },
    ],
    "qa": [
        {
            "title": "Составить тест-план по ключевым сценариям",
            "description": "Описать smoke, regression и acceptance сценарии для MVP.",
            "skills": ["qa", "test design", "manual testing"],
            "category": "qa",
        },
        {
            "title": "Написать автотесты для критичных сценариев",
            "description": "Покрыть логин, создание сущностей и основные пользовательские пути.",
            "skills": ["qa automation", "pytest", "api testing"],
            "category": "qa",
        },
    ],
    "analytics": [
        {
            "title": "Определить продуктовые метрики",
            "description": "Выбрать North Star metric, activation, retention и технические KPI.",
            "skills": ["analytics", "product metrics", "sql"],
            "category": "analytics",
        },
        {
            "title": "Настроить события аналитики",
            "description": "Собрать схему событий, naming и базовые дашборды по воронке.",
            "skills": ["analytics", "event tracking", "dashboarding"],
            "category": "analytics",
        },
    ],
    "ml": [
        {
            "title": "Подготовить рекомендации на основе эмбеддингов",
            "description": "Построить эмбеддинги объектов и вычислять похожие элементы для персонализации.",
            "skills": ["machine learning", "python", "embeddings"],
            "category": "ml",
        },
        {
            "title": "Настроить поиск по смыслу",
            "description": "Реализовать semantic search по объектам продукта и результатам пользователей.",
            "skills": ["nlp", "semantic search", "embeddings"],
            "category": "ml",
        },
    ],
}


TEAM_MEMBERS = [
    {
        "id": "U001",
        "name": "Аня Ковалева",
        "role": "Product Manager",
        "skills": ["product management", "prioritization", "backlog management", "research", "roadmapping"],
        "secondary_skills": ["analytics", "presentation", "stakeholder management"],
        "availability_hours_per_week": 16,
    },
    {
        "id": "U002",
        "name": "Илья Смирнов",
        "role": "Business Analyst",
        "skills": ["research", "customer development", "requirements", "documentation", "user stories"],
        "secondary_skills": ["product discovery", "analytics", "sql"],
        "availability_hours_per_week": 14,
    },
    {
        "id": "U003",
        "name": "Маша Белова",
        "role": "UX/UI Designer",
        "skills": ["ux design", "ui design", "figma", "design systems", "information architecture"],
        "secondary_skills": ["prototyping", "user flow", "branding"],
        "availability_hours_per_week": 18,
    },
    {
        "id": "U004",
        "name": "Егор Павлов",
        "role": "Frontend Engineer",
        "skills": ["react", "typescript", "frontend", "state management", "api integration"],
        "secondary_skills": ["next.js", "performance", "form validation"],
        "availability_hours_per_week": 20,
    },
    {
        "id": "U005",
        "name": "София Громова",
        "role": "Frontend Engineer",
        "skills": ["react", "typescript", "frontend", "design systems", "testing library"],
        "secondary_skills": ["accessibility", "css", "api integration"],
        "availability_hours_per_week": 18,
    },
    {
        "id": "U006",
        "name": "Данил Жуков",
        "role": "Backend Engineer",
        "skills": ["python", "fastapi", "api development", "sql", "database design"],
        "secondary_skills": ["backend architecture", "authentication", "pytest"],
        "availability_hours_per_week": 20,
    },
    {
        "id": "U007",
        "name": "Никита Орлов",
        "role": "Backend Engineer",
        "skills": ["node.js", "postgresql", "api development", "security", "backend"],
        "secondary_skills": ["authentication", "redis", "backend architecture"],
        "availability_hours_per_week": 16,
    },
    {
        "id": "U008",
        "name": "Полина Миронова",
        "role": "Mobile Engineer",
        "skills": ["flutter", "mobile", "mobile ui", "firebase", "state management"],
        "secondary_skills": ["android", "push notifications", "api integration"],
        "availability_hours_per_week": 16,
    },
    {
        "id": "U009",
        "name": "Тимур Каримов",
        "role": "Data Scientist",
        "skills": ["machine learning", "python", "embeddings", "nlp", "semantic search"],
        "secondary_skills": ["recommender systems", "pandas", "evaluation"],
        "availability_hours_per_week": 14,
    },
    {
        "id": "U010",
        "name": "Вика Романова",
        "role": "Data Analyst",
        "skills": ["analytics", "sql", "dashboarding", "product metrics", "event tracking"],
        "secondary_skills": ["a/b testing", "visualization", "experiments"],
        "availability_hours_per_week": 14,
    },
    {
        "id": "U011",
        "name": "Артем Седов",
        "role": "DevOps Engineer",
        "skills": ["devops", "docker", "github actions", "linux", "deployment"],
        "secondary_skills": ["monitoring", "cloud", "ci/cd"],
        "availability_hours_per_week": 15,
    },
    {
        "id": "U012",
        "name": "Ксения Фролова",
        "role": "QA Engineer",
        "skills": ["qa", "manual testing", "test design", "regression testing", "acceptance testing"],
        "secondary_skills": ["bug reporting", "checklists", "usability testing"],
        "availability_hours_per_week": 15,
    },
    {
        "id": "U013",
        "name": "Руслан Виноградов",
        "role": "QA Automation Engineer",
        "skills": ["qa automation", "pytest", "api testing", "selenium", "python"],
        "secondary_skills": ["ci/cd", "test strategy", "quality gates"],
        "availability_hours_per_week": 14,
    },
    {
        "id": "U014",
        "name": "Лера Демина",
        "role": "Fullstack Engineer",
        "skills": ["react", "python", "fastapi", "frontend", "api development"],
        "secondary_skills": ["sql", "docker", "authentication"],
        "availability_hours_per_week": 18,
    },
    {
        "id": "U015",
        "name": "Максим Титов",
        "role": "Product Designer",
        "skills": ["ui design", "figma", "branding", "prototyping", "design systems"],
        "secondary_skills": ["ux design", "presentation", "motion design"],
        "availability_hours_per_week": 12,
    },
    {
        "id": "U016",
        "name": "Оля Нестерова",
        "role": "Growth Analyst",
        "skills": ["analytics", "event tracking", "dashboarding", "visualization", "growth"],
        "secondary_skills": ["sql", "product metrics", "experiments"],
        "availability_hours_per_week": 12,
    },
    {
        "id": "U017",
        "name": "Саша Лебедев",
        "role": "Backend / Security",
        "skills": ["backend", "security", "authentication", "python", "api development"],
        "secondary_skills": ["owasp", "database design", "monitoring"],
        "availability_hours_per_week": 12,
    },
    {
        "id": "U018",
        "name": "Катя Власова",
        "role": "Project Coordinator",
        "skills": ["project management", "documentation", "communication", "planning", "risk management"],
        "secondary_skills": ["backlog management", "research", "stakeholder management"],
        "availability_hours_per_week": 10,
    },
]


def choose_tasks(rng, product):
    tasks = []
    tasks.extend(rng.sample(TASK_BLUEPRINTS["discovery"], k=2))
    tasks.extend(rng.sample(TASK_BLUEPRINTS["design"], k=2))
    tasks.extend(rng.sample(TASK_BLUEPRINTS["backend"], k=3))
    tasks.extend(rng.sample(TASK_BLUEPRINTS["frontend"], k=3))
    tasks.extend(rng.sample(TASK_BLUEPRINTS["devops"], k=2))
    tasks.extend(rng.sample(TASK_BLUEPRINTS["qa"], k=2))
    tasks.extend(rng.sample(TASK_BLUEPRINTS["analytics"], k=2))

    if product["domain"] in {"edtech", "career", "creator"} or rng.random() > 0.55:
        tasks.extend(rng.sample(TASK_BLUEPRINTS["ml"], k=2))

    if product["domain"] in {"community", "foodtech", "productivity"} or rng.random() > 0.6:
        tasks.extend(rng.sample(TASK_BLUEPRINTS["mobile"], k=2))

    rng.shuffle(tasks)
    return tasks


def build_project(rng, index):
    product = rng.choice(PRODUCT_TYPES)
    feature_focus = rng.sample(product["features"], k=2)
    title = f"{product['name'].capitalize()} #{index:03d}"
    description = (
        f"{product['name'].capitalize()} для {product['audience']}. "
        f"Ключевой фокус MVP: {feature_focus[0]}, {feature_focus[1]} и стабильный user flow."
    )
    tasks = []

    for task_index, task in enumerate(choose_tasks(rng, product), start=1):
        difficulty = rng.choice(["low", "medium", "high"])
        hours = {"low": rng.randint(4, 8), "medium": rng.randint(8, 16), "high": rng.randint(16, 28)}[difficulty]
        tasks.append(
            {
                "id": f"P{index:03d}-T{task_index:02d}",
                "title": task["title"],
                "description": (
                    f"{task['description']} Контекст проекта: {product['name']} для {product['audience']}, "
                    f"важны функции {', '.join(feature_focus)}."
                ),
                "required_skills": task["skills"],
                "category": task["category"],
                "difficulty": difficulty,
                "estimated_hours": hours,
                "priority": rng.choice(["must_have", "should_have", "nice_to_have"]),
            }
        )

    return {
        "id": f"P{index:03d}",
        "title": title,
        "description": description,
        "domain": product["domain"],
        "target_audience": product["audience"],
        "core_features": feature_focus,
        "tasks": tasks,
    }


def enrich_team(rng):
    members = []
    for member in TEAM_MEMBERS:
        members.append(
            {
                **member,
                "current_load_hours": rng.randint(0, 12),
                "max_parallel_tasks": rng.randint(2, 4),
                "bio": (
                    f"{member['role']} со стеком {', '.join(member['skills'][:4])}. "
                    f"Дополнительно силен в {', '.join(member['secondary_skills'][:2])}."
                ),
            }
        )
    return members


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    rng = random.Random(SEED)
    root = Path(__file__).resolve().parent
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    projects = [build_project(rng, index) for index in range(1, PROJECTS_COUNT + 1)]
    team = enrich_team(rng)

    (data_dir / "projects.json").write_text(
        json.dumps(projects, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (data_dir / "team.json").write_text(
        json.dumps(team, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Generated {len(projects)} projects and {len(team)} team members in {data_dir}")


if __name__ == "__main__":
    main()
