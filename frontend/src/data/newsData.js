import { assets } from "../assets";

export const MINI_NEWS_ITEMS = [
  {
    id: "yandex-frontend-meetup",
    title: "Недавно Яндекс провел митап по фронтенду, а также бесплатные вебинары по JavaScript и TypeScript",
    imageUrl: assets.newsPhoto,
    detailsUrl: "/news/yandex-frontend-meetup"
  },
  {
    id: "hse-startup-cup",
    title: "Недавно ВШЭ провел конкурс стартапов среди студентов и сотрудников университета",
    imageUrl: assets.posterHackathon,
    detailsUrl: "/news/hse-startup-cup"
  },
  {
    id: "ds-academy-open",
    title: "В Центральном университете открыли академию Data Science",
    imageUrl: assets.posterTechConf,
    detailsUrl: "/news/ds-academy-open"
  },
  {
    id: "neuroscale-launch",
    title: "NeuroScale представил новый курс по разработке ИИ-сервисов на Yandex Cloud",
    imageUrl: assets.posterWeb3,
    detailsUrl: "/news/neuroscale-launch"
  }
];

export const FEATURED_NEWS_ITEMS = [
  {
    id: "students-ideathon",
    title: "Идеатон для студентов",
    subtitle: "Высшая школа экономики",
    description:
      "В рамках идеатона участникам двух треков предстоит разработать концепт продукта и презентацию, применив навыки работы в команде, умение анализировать конкурентов и способность находить нестандартные решения.",
    imageUrl: assets.posterTechTalk,
    ctaLabel: "Участвовать",
    detailsUrl: "/events/students-ideathon"
  },
  {
    id: "sber-hackathon",
    title: "Хакатон от Сбера",
    subtitle: "Высшая школа экономики x SBER",
    description:
      "Участникам хакатона нужно собрать MVP за 48 часов, подготовить демо и защитить решение перед жюри из индустрии.",
    imageUrl: assets.posterTechConf,
    ctaLabel: "Участвовать",
    detailsUrl: "/events/sber-hackathon"
  }
];

function normalizeString(value, fallback) {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }
  return fallback;
}

export function mapApiMiniNews(items = []) {
  return items.map((item, index) => ({
    id: normalizeString(item.id, `mini-news-${index}`),
    title: normalizeString(item.title, "Без названия"),
    imageUrl: normalizeString(item.imageUrl, ""),
    detailsUrl: normalizeString(item.detailsUrl, "/news")
  }));
}

export function mapApiFeaturedNews(items = []) {
  return items.map((item, index) => ({
    id: normalizeString(item.id, `featured-news-${index}`),
    title: normalizeString(item.title, "Без названия"),
    subtitle: normalizeString(item.subtitle, ""),
    description: normalizeString(item.description, ""),
    imageUrl: normalizeString(item.imageUrl, ""),
    ctaLabel: normalizeString(item.ctaLabel, "Участвовать"),
    detailsUrl: normalizeString(item.detailsUrl, "/events"),
    participated: Boolean(item.participated)
  }));
}
