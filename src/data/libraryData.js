import { assets } from "../assets";

export const LIBRARY_HERO_RESOURCE = {
  id: "ml-engineer-course",
  title: "Курс «ML-инженер»",
  updatedLabel: "3 дня назад",
  providerLabel: "Яндекс практикум",
  description:
    "За 12 месяцев освоите востребованную профессию и получите реальный опыт: пройдёте полный цикл ML-проекта — от подготовки данных и обучения моделей до внедрения и поддержки"
};

export const LIBRARY_SHOWCASE_ITEMS = [
  {
    id: "netology-ml-engineer",
    brandLabel: "нетология",
    eyebrow: "Профессия",
    title: "ML-инженер",
    imageUrl: assets.poster120Image
  },
  {
    id: "practicum-mlops",
    brandLabel: "Яндекс практикум",
    eyebrow: "Интенсив",
    title: "MLOps и продакшн",
    imageUrl: assets.posterTechTalk
  },
  {
    id: "skillbox-data-analyst",
    brandLabel: "Skillbox",
    eyebrow: "Профессия",
    title: "Data Analyst",
    imageUrl: assets.posterTechConf
  }
];

export const LIBRARY_INTEREST_OPTIONS = [
  { id: "ml-engineering", label: "ML инженеринг", selected: true },
  { id: "ux-ui", label: "UX/UI дизайн", selected: false },
  { id: "frontend", label: "Frontend stack", selected: false },
  { id: "backend", label: "Backend stack", selected: false },
  { id: "testing", label: "#Тестировка", selected: false },
  { id: "qa-courses", label: "#QA курсы", selected: false }
];

export function createInitialLibraryInterestState() {
  return LIBRARY_INTEREST_OPTIONS.reduce((acc, item) => ({ ...acc, [item.id]: Boolean(item.selected) }), {});
}

export const LIBRARY_ARTICLE_ITEMS = [
  {
    id: "go-python-fullstack",
    tags: [
      { id: "python", label: "#Python", tone: "green" },
      { id: "golang", label: "#GoLang", tone: "cyan" },
      { id: "fullstack", label: "#FullStack", tone: "coral" }
    ],
    title: "Fullstack проект на Go и python",
    description:
      "По ходу статьи эксперты рассказывают про типичные инженерные вещи — тестирование, прикладную бизнес-логику и интеграцию компонентов.",
    authorName: "PythonGo PRO",
    authorAvatarUrl: assets.avatarPhoto
  },
  {
    id: "catboost-xgboost-trees",
    tags: [
      { id: "python", label: "#Python", tone: "green" },
      { id: "ml", label: "#ML", tone: "yellow" }
    ],
    title: "CatBoost, XGBoost + деревья",
    description:
      "Данный обзор охватывает сразу несколько тем. Мы начнём с устройства решающего дерева и градиентного бустинга, затем подробно поговорим об XGBoost и CatBoost.",
    authorName: "Top MLman",
    authorAvatarUrl: assets.avatarPhoto
  },
  {
    id: "neural-generation-comparison",
    tags: [
      { id: "python", label: "#Python", tone: "green" },
      { id: "ai", label: "#AI", tone: "pink" },
      { id: "gen-model", label: "#generation model", tone: "blue" }
    ],
    title: "Сравнение нейросетей в генерациях",
    description:
      "По ходу статьи эксперты рассказывают про типичные инженерные вещи — тестирование, прикладную бизнес-логику и интеграцию компонентов.",
    authorName: "MaxabouAI",
    authorAvatarUrl: assets.avatarPhoto
  }
];
