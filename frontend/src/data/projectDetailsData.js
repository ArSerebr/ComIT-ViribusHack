import { assets } from "../assets";

function createPerson(id, name, avatarVariant, extra = {}) {
  return {
    id,
    name,
    avatarUrl: assets.avatarPhoto,
    avatarVariant,
    ...extra
  };
}

export const PROJECT_DETAILS_BY_ID = {
  "api-food-delivery": {
    id: "api-food-delivery",
    code: "#TF9876",
    title: "API для доставки еды",
    ownerName: "Frontend Pro",
    detailsUrl: "/projects/api-food-delivery",
    joinLabel: "Присоединиться в команду",
    teamCaption: "Все участники проекта",
    productivityCaption: "Статистика за последний месяц",
    progressCaption: "Какая часть уже готова",
    todoCaption: "Последние задачи в проекте",
    integrationCaption: "Подключайте сервисы для комфортной работы в команде",
    teamMembersPreview: [
      createPerson("maksdev", "maksDEV", "default"),
      createPerson("backend-lead", "daniil", "warm"),
      createPerson("ux-designer", "liza", "cool")
    ],
    productivity: {
      value: "80%",
      delta: "+15% за месяц"
    },
    progress: {
      value: "40%",
      percent: 40
    },
    todo: {
      task: "Завершить расчёт LTV, ARPU и CAC",
      updatedLabel: "2 часа назад"
    },
    integrations: [
      {
        id: "github",
        brand: "github",
        description: "Автоматический деплой кода",
        statusLabel: "Подключено",
        connectedSince: "с 17.02.2026"
      },
      {
        id: "timeweb",
        brand: "timeweb",
        description: "Хостинг ваших проектов",
        statusLabel: "Подключено",
        connectedSince: "с 31.01.2026"
      }
    ],
    participants: [
      createPerson("maksdev-row", "maksDEV", "default", {
        comitId: "#78654",
        timeInProject: "255 мин",
        role: "Backend-разработчик",
        status: "Работает",
        lastTask: "Настройка ORM"
      }),
      createPerson("daniil-row", "daniilUI", "warm", {
        comitId: "#56342",
        timeInProject: "193 мин",
        role: "UX/UI дизайнер",
        status: "Работает",
        lastTask: "Доработка wireframes"
      }),
      createPerson("liza-row", "lizaQA", "cool", {
        comitId: "#90187",
        timeInProject: "148 мин",
        role: "QA-инженер",
        status: "Работает",
        lastTask: "Проверка сценариев заказа"
      })
    ]
  }
};
