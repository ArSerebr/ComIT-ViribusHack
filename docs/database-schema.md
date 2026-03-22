# Схема базы данных (PostgreSQL)

База данных проекта описана миграциями Alembic в `backend/alembic/versions/` и ORM-моделями в `backend/app/modules/*/models.py`. Ниже — обзор по доменам и диаграмма в формате [DBML](https://dbml.dbdiagram.io/docs) для [dbdiagram.io](https://dbdiagram.io).

## Обзор по модулям

| Модуль | Таблицы | Назначение |
|--------|---------|------------|
| **auth** | `user` | Пользователи (fastapi-users: email, пароль, флаги) + роль (`user` / `moderator` / `admin`) |
| **profile** | `user_profile`, `user_profile_interest`, `profile_university` | Профиль (имя, био, университет) и связь пользователя с опциями интересов из библиотеки; справочник университетов |
| **projects** | `projects_column`, `projects_project`, `projects_project_detail` | Канбан-колонки, карточки проектов, детальная страница (JSON-блоки) |
| **library** | `library_showcase_item`, `library_interest_option`, `library_article`, `library_tag`, `library_article_tag` | Витрина, опции интересов, статьи, теги, связь статья–тег |
| **news** | `news_mini`, `news_featured` | Мини-новости и крупные новости |
| **notifications** | `notifications_item` | Элементы ленты уведомлений (без FK на пользователя в текущей схеме) |
| **dashboard** | `dashboard_recommendation`, `dashboard_home_snapshot` | Рекомендации на главной; singleton-снимок JSON для home |
| **analytics** | `analytics_like_event`, `analytics_interest_event`, `analytics_join_request` | Лайки по сущностям, выбор интересов, заявки на вступление в проект |

## Связи (кратко)

- `user` ← `user_profile` (1:1), `user_profile_interest` (M:N с `library_interest_option`). `user_profile.university_id` → `profile_university.id` (опционально, `ON DELETE SET NULL`).
- `user` ← `projects_project.owner_user_id`, `library_article.owner_user_id`, `news_mini.author_user_id`, `news_featured.author_user_id` (все опционально, `ON DELETE SET NULL`).
- `projects_column` → `projects_project` (`RESTRICT`); `projects_project` → `projects_project_detail` и `analytics_join_request` (`CASCADE`).
- `library_article` ↔ `library_tag` через `library_article_tag` (`CASCADE` / `RESTRICT` на тег).

## Индексы (из миграций)

- Уникальный: `user.email` (`ix_user_email`).
- Составной: `projects_project` (`column_id`, `sort_order`) — `ix_projects_project_column_sort`.
- Внешние ключи: `ix_projects_project_owner_user_id`, `ix_library_article_owner_user_id`, `ix_news_mini_author_user_id`, `ix_news_featured_author_user_id`.
- Связующие: `ix_library_article_tag_tag_id`, `ix_user_profile_interest_interest_id`, `ix_user_profile_university_id`.

---

## DBML для dbdiagram.io

Скопируйте блок ниже в [dbdiagram.io](https://dbdiagram.io/d) (Import → DBML) или в расширение DBML для VS Code.

```dbml
// PostgreSQL — ComIT Viribus Hack
// Источник: backend alembic + SQLAlchemy models

Project viribus {
  database_type: 'PostgreSQL'
  Note: 'Схема согласована с миграциями f04f0693ddd6, 7c2b9a1a2f4d, 8f3a9c1e2b04, 9e4b1d7a3c55'
}

Table "user" {
  id uuid [pk, note: 'PK']
  email varchar(320) [not null, unique, note: 'ix_user_email']
  hashed_password varchar(1024) [not null]
  is_active boolean [not null, default: true]
  is_superuser boolean [not null, default: false]
  is_verified boolean [not null, default: false]
  role varchar(32) [not null, default: 'user']

  Note: 'fastapi-users + role'
}

Table profile_university {
  id varchar(64) [pk]
  name varchar(255) [not null]
  sort_order integer [not null, default: 0]

  Note: 'Справочник университетов'
}

Table user_profile {
  user_id uuid [pk, ref: - "user".id]
  display_name varchar(255)
  bio text
  university_id varchar(64) [ref: > profile_university.id, null]

  indexes {
    university_id [name: 'ix_user_profile_university_id']
  }
}

Table library_interest_option {
  id varchar(64) [pk]
  label varchar(255) [not null]
  selected boolean [not null]
  sort_order integer [not null, default: 0]
}

Table user_profile_interest {
  user_id uuid [pk, ref: > "user".id]
  interest_id varchar(64) [pk, ref: > library_interest_option.id]

  indexes {
    interest_id [name: 'ix_user_profile_interest_interest_id']
  }
}

Table projects_column {
  id varchar(64) [pk]
  title varchar(255) [not null]
  sort_order integer [not null, default: 0]
}

Table projects_project {
  id varchar(255) [pk]
  code varchar(32) [not null]
  title text [not null]
  description text [not null]
  team_name varchar(255) [not null]
  updated_label varchar(255) [not null]
  team_avatar_url varchar(2048) [not null]
  details_url varchar(2048) [not null]
  visibility varchar(20)
  is_hot boolean
  column_id varchar(64) [not null, ref: > projects_column.id]
  sort_order integer [not null, default: 0]
  owner_user_id uuid [ref: > "user".id, null]

  indexes {
    (column_id, sort_order) [name: 'ix_projects_project_column_sort']
    owner_user_id [name: 'ix_projects_project_owner_user_id']
  }
}

Table projects_project_detail {
  project_id varchar(255) [pk, ref: - projects_project.id]
  owner_name varchar(255) [not null]
  join_label varchar(255) [not null]
  team_caption varchar(255) [not null]
  productivity_caption varchar(255) [not null]
  progress_caption varchar(255) [not null]
  todo_caption varchar(255) [not null]
  integration_caption varchar(255) [not null]
  detail_blocks jsonb [not null]
}

Table analytics_like_event {
  id bigint [pk, increment]
  entity varchar(20) [not null]
  entity_id varchar(255) [not null]
  ts bigint [not null]
  seed_key varchar(255) [unique, note: 'для идемпотентного seed']
}

Table analytics_interest_event {
  id bigint [pk, increment]
  interests text[] [not null]
  ts bigint [not null]
}

Table analytics_join_request {
  id bigint [pk, increment]
  project_id varchar(255) [not null, ref: > projects_project.id]
  message text
  created_at timestamptz [not null, default: `now()`]
}

Table dashboard_home_snapshot {
  id smallint [pk, note: 'ожидается singleton id=1']
  home_json jsonb [not null]
}

Table dashboard_recommendation {
  id varchar(255) [pk]
  title text [not null]
  subtitle text [not null]
  image varchar(2048) [not null]
  link varchar(2048) [not null]
  sort_order integer [not null, default: 0]
}

Table library_showcase_item {
  id varchar(255) [pk]
  brand_label varchar(255) [not null]
  eyebrow varchar(255) [not null]
  title text [not null]
  image_url varchar(2048) [not null]
  hero_json jsonb [not null]
  sort_order integer [not null, default: 0]
}

Table library_article {
  id varchar(255) [pk]
  title text [not null]
  description text [not null]
  author_name varchar(255) [not null]
  author_avatar_url varchar(2048) [not null]
  owner_user_id uuid [ref: > "user".id, null]

  indexes {
    owner_user_id [name: 'ix_library_article_owner_user_id']
  }
}

Table library_tag {
  id varchar(64) [pk]
  label varchar(255) [not null]
  tone varchar(64) [not null]
  sort_order integer
}

Table library_article_tag {
  article_id varchar(255) [pk, ref: > library_article.id]
  tag_id varchar(64) [pk, ref: > library_tag.id]
  position integer [not null, default: 0]

  indexes {
    tag_id [name: 'ix_library_article_tag_tag_id']
  }
}

Table news_mini {
  id varchar(255) [pk]
  title text [not null]
  image_url varchar(2048) [not null]
  details_url varchar(2048) [not null]
  sort_order integer [not null, default: 0]
  author_user_id uuid [ref: > "user".id, null]

  indexes {
    author_user_id [name: 'ix_news_mini_author_user_id']
  }
}

Table news_featured {
  id varchar(255) [pk]
  title text [not null]
  subtitle text [not null]
  description text [not null]
  image_url varchar(2048) [not null]
  cta_label varchar(255) [not null]
  details_url varchar(2048) [not null]
  sort_order integer [not null, default: 0]
  author_user_id uuid [ref: > "user".id, null]

  indexes {
    author_user_id [name: 'ix_news_featured_author_user_id']
  }
}

Table notifications_item {
  id varchar(255) [pk]
  type varchar(64) [not null]
  title text [not null]
  date_label varchar(255) [not null]
  date_caption varchar(255) [not null]
  unread boolean
  author_label varchar(255)
  author_name varchar(255)
  accent_text varchar(255)
  cta_label varchar(255)
  path varchar(2048)
  sort_order integer [not null, default: 0]
}
```

### Примечания к DBML

- Таблица `user` в PostgreSQL зарезервирована; в DBML она указана как `"user"`.
- Синтаксис индексов и `ref` в DBML может слегка отличаться в зависимости от версии редактора; при ошибке импорта упростите блок `indexes { ... }` или опишите связи только через `Ref:` (см. [документацию DBML](https://dbml.dbdiagram.io/docs)).
- Действия `ON DELETE` в PostgreSQL заданы в Alembic; в DBML для inline-`ref` не задаются — см. раздел «Связи» выше и миграции.
- Типы `jsonb`, `text[]`, `timestamptz` соответствуют миграциям и SQLAlchemy.

## Порядок миграций Alembic

1. `f04f0693ddd6` — начальная схема (без `user`).
2. `7c2b9a1a2f4d` — таблица `user`.
3. `8f3a9c1e2b04` — `user_profile`, `user_profile_interest`.
4. `9e4b1d7a3c55` — `owner_user_id` / `author_user_id` на проектах, library и news.
