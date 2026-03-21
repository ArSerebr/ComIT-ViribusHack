import { assets } from "../assets";

function withDefaults(column) {
  return {
    ...column,
    count: column.projects.length,
    projects: column.projects.map((project) => ({
      ...project,
      teamAvatarUrl: project.teamAvatarUrl || assets.avatarPhoto,
      detailsUrl: project.detailsUrl || `/projects/${project.id}`,
      visibility: project.visibility || null
    }))
  };
}

export const PROJECT_HUB_COLUMNS = [
  {
    id: "idea",
    title: "На стадии идеи",
    projects: [
      {
        id: "api-food-delivery",
        code: "#TF9876",
        visibility: "public",
        title: "API для доставки еды",
        isHot: true,
        description: "Мы с командой разрабатываем систему для доставки еды, пока нам нужен UX/UI дизайнер",
        teamName: "Frontend PRO",
        updatedLabel: "3 дня назад"
      },
      {
        id: "odyssey-ai",
        code: "#TF9217",
        visibility: "public",
        title: "ODYSSEY AI",
        description: "Хотим сделать AI для создания качественных презентаций и быстрого сторителлинга",
        teamName: "Frontend PRO",
        updatedLabel: "5 дней назад"
      },
      {
        id: "campus-event-hub",
        code: "#TF9012",
        visibility: "public",
        title: "Campus Event Hub",
        description: "Платформа для организации университетских ивентов с ролями, слотами и заявками",
        teamName: "IdeaSprint",
        updatedLabel: "1 неделю назад"
      }
    ]
  },
  {
    id: "development",
    title: "В разработке",
    projects: [
      {
        id: "microservice-architecture",
        code: "#EK9764",
        visibility: "private",
        title: "Архитектура для микросервиса",
        description: "Мы с командой разрабатываем систему для доставки еды, пока нам нужен UX/UI дизайнер",
        teamName: "GOMAKSTEAM",
        updatedLabel: "1 месяц назад"
      },
      {
        id: "study-sync",
        code: "#EK9811",
        visibility: "private",
        title: "StudySync",
        description: "Собираем единое рабочее пространство для учебных команд с задачами и файлами",
        teamName: "GOMAKSTEAM",
        updatedLabel: "2 недели назад"
      },
      {
        id: "ml-notes-api",
        code: "#EK9450",
        visibility: "private",
        title: "ML Notes API",
        description: "Строим API и пайплайн для персональных конспектов по курсам и AI-поиска по ним",
        teamName: "Core Unit",
        updatedLabel: "6 дней назад"
      },
      {
        id: "hack-ai-studio",
        code: "#EK9635",
        visibility: "private",
        title: "Hack AI Studio",
        description: "Делаем конструктор прототипов для хакатонов с шаблонами фич и аналитикой",
        teamName: "MVP Crew",
        updatedLabel: "9 дней назад"
      }
    ]
  },
  {
    id: "integrated",
    title: "Интегрированные",
    projects: [
      {
        id: "sensitive-llm",
        code: "#KN2314",
        title: "Sensitive LLM",
        description: "Мы с командой разрабатываем систему для доставки еды, пока нам нужен UX/UI дизайнер",
        teamName: "AI_dev_team32",
        updatedLabel: "2 месяца назад"
      },
      {
        id: "edugramm",
        code: "#KN2482",
        title: "EdugraMM",
        isHot: true,
        description: "Мы с командой разрабатываем систему для доставки еды, пока нам нужен UX/UI дизайнер",
        teamName: "AI_dev_team32",
        updatedLabel: "2 месяца назад"
      },
      {
        id: "mentors-match",
        code: "#KN2674",
        title: "Mentors Match",
        description: "Сервис рекомендаций для подбора менторов и проектных команд внутри вуза",
        teamName: "Campus Core",
        updatedLabel: "3 месяца назад"
      },
      {
        id: "dev-portfolio-loop",
        code: "#KN2539",
        title: "Dev Portfolio Loop",
        description: "Автоматизируем сбор артефактов по проекту и упаковку их в живое портфолио",
        teamName: "Portfolio Lab",
        updatedLabel: "3 месяца назад"
      },
      {
        id: "startup-radar",
        code: "#KN2781",
        title: "Startup Radar",
        description: "Лента университетских стартапов с витриной метрик, статусов и командного состава",
        teamName: "Launch Team",
        updatedLabel: "4 месяца назад"
      }
    ]
  }
].map(withDefaults);
