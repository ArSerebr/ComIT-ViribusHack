import { assets } from "../assets";

export const MENU_ITEMS = [
  {
    id: "home",
    label: "Главная",
    icons: { active: assets.mainActiveIcon, inactive: assets.mainInactiveIcon }
  },
  {
    id: "ai",
    label: "Чат с ИИ",
    icons: { active: assets.aiActiveIcon, inactive: assets.aiInactiveIcon }
  },
  {
    id: "projects",
    label: "Проекты",
    icons: { active: assets.projectsActiveIcon, inactive: assets.projectsInactiveIcon }
  },
  {
    id: "news",
    label: "Ивенты",
    icons: { active: assets.newsActiveIcon, inactive: assets.newsInactiveIcon }
  },
  {
    id: "library",
    label: "Библиотека",
    icons: { active: assets.libraryActiveIcon, inactive: assets.libraryInactiveIcon }
  }
];

export const RECOMMENDATIONS = [
  {
    id: "hackathon",
    title: "Хакатон 2026",
    subtitle: "Погружение в ML + Frontend",
    image: assets.posterHackathon,
    link: "https://example.com/hackathon"
  },
  {
    id: "web3",
    title: "Web3 Design",
    subtitle: "Интенсив по продукту",
    image: assets.posterWeb3,
    link: "https://example.com/web3-design"
  },
  {
    id: "tech-conf",
    title: "Tech Conference",
    subtitle: "Frontend engineering",
    image: assets.posterTechConf,
    link: "https://example.com/tech-conference"
  },
  {
    id: "tech-talk",
    title: "Tech Talk",
    subtitle: "Современный стек разработчика",
    image: assets.posterTechTalk,
    link: "https://example.com/tech-talk"
  }
];

export const INITIAL_CHAT = [
  {
    id: "m-1",
    role: "assistant",
    content:
      "Привет. Я **ComIT AI**.\n\nМогу помочь:\n- подобрать курс\n- разобрать roadmap\n- собрать стек под цель",
    actions: [
      { label: "Подобрать курс", prompt: "Подбери мне курс по ML на 3 месяца" },
      { label: "Собрать roadmap", prompt: "Собери roadmap для Junior Frontend" }
    ]
  }
];

export const QUICK_PROMPTS = ["Главные новости IT", "Есть ли хакатоны от Т-Банка?"];

export const NAV_LINKS = {
  courses: "/courses",
  events: "/events",
  projects: "/projects",
  news: "/news",
  chat: "/chat"
};
