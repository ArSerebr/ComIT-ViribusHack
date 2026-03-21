import { assets } from "../assets";

export const ARTICLE_DETAILS_BY_SLUG = {
  "ml-ab-tests": {
    id: "ml-ab-tests",
    slug: "ml-ab-tests",
    title: "ML-критерии для A/B-тестов",
    updatedLabel: "3 дня назад",
    viewsLabel: "23K",
    summary:
      "Разбираем CUPED-подход и связанные ML-критерии, которые помогают повысить чувствительность A/B-тестов и быстрее принимать решения.",
    paragraphs: [
      "Всем привет! Меня зовут Дима Лунин, и я аналитик в Авито. Как и в большинстве компаний, основной инструмент для принятия решений в продукте — это A/B-тесты. Чтобы эксперимент был полезным, нам важно не только корректно выбрать критерий, но и сделать результат устойчивым к шуму.",
      "В этом материале я покажу практический разбор методов, которые повышают мощность эксперимента и улучшают интерпретируемость выводов. По ходу текста будем опираться на реальные кейсы команды и на типовые ошибки, с которыми обычно сталкиваются аналитики.",
      "Основной акцент сделан на комбинации классических статистических подходов и ML-моделей. Такой гибридный подход помогает учитывать структуру пользовательских данных, а также снизить риск ложноположительных решений на небольших выборках."
    ],
    points: [
      "Что такое CUPED-метод и где он особенно полезен.",
      "Как улучшить CUPED-алгоритм: CUPAC, CUNOPAC и CUMPED.",
      "Как использовать uplift-модели в качестве статистического критерия.",
      "Когда стоит комбинировать несколько критериев одновременно.",
      "В каких сценариях стратификация и обычный CUPED работают лучше всего."
    ],
    heroImageUrl: assets.posterTechConf,
    relatedCourseSlug: "machine-learning-from-zero"
  }
};

export const COURSE_DETAILS_BY_SLUG = {
  "machine-learning-from-zero": {
    id: "machine-learning-from-zero",
    slug: "machine-learning-from-zero",
    categoryLabels: ["Анализ данных", "Искусственный интеллект"],
    title: "Инженер машинного обучения с нуля",
    summary:
      "За 4 месяца освоите полный жизненный цикл модели машинного обучения и сможете строить продвинутые ML-модели.",
    outcomes: [
      "Старт в профессии и комплексные навыки для работы: от создания до внедрения и поддержки ML-моделей.",
      "10+ проектов для практики, кейсы от партнеров и диплом по своей или учебной теме.",
      "Поддержка ML-инженеров из Яндекса, Сбера, Amazon и других компаний в течение всего обучения."
    ],
    ctaLabel: "Перейти на сайт",
    providerName: "Нетология",
    providerTrack: "Профессия",
    providerTitle: "ML-инженер",
    providerImageUrl: assets.poster120Image
  }
};

export const ARTICLE_SIDE_RECOMMENDATIONS = [
  {
    id: "hackathon-2026",
    title: "Hackathon",
    subtitle: "Qisanti 2026",
    imageUrl: assets.posterHackathon,
    badgeLabel: "New"
  },
  {
    id: "uni-joy",
    title: "UNI_JOY4E",
    subtitle: "Кампус-ивент",
    imageUrl: assets.posterWeb3
  },
  {
    id: "frontend-meetup",
    title: "Митап по фронтенду",
    subtitle: "JavaScript и TypeScript",
    imageUrl: assets.newsPhoto,
    compact: true,
    detailsUrl: "/news/yandex-frontend-meetup"
  }
];
