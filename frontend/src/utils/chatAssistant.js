export function nextAssistantMessage(text) {
  const normalized = text.toLowerCase();

  if (normalized.includes("ml")) {
    return {
      content:
        "### План по ML на 3 месяца\\n\\n1. Python + NumPy/Pandas\\n2. Классические модели\\n3. Pet-проект с деплоем\\n\\n`Совет:` фиксируй прогресс каждую неделю.",
      actions: [
        { label: "Дай курсы", prompt: "Покажи 3 курса по ML для новичка" },
        { label: "Нужен проект", prompt: "Дай идею pet-проекта для ML портфолио" }
      ]
    };
  }

  if (normalized.includes("frontend") || normalized.includes("стек")) {
    return {
      content:
        "Рекомендуемый **Frontend-стек**:\\n\\n- `HTML/CSS`\\n- `JavaScript`\\n- `React`\\n- `TypeScript`\\n- `Vite`\\n\\nПосле этого переходи к тестам (`Vitest`, `Playwright`).",
      actions: [{ label: "Roadmap на 8 недель", prompt: "Сделай roadmap frontend на 8 недель" }]
    };
  }

  return {
    content:
      "Принял запрос. Могу развернуть ответ в виде:\\n\\n- подробного плана\\n- списка ресурсов\\n- практического задания",
    actions: [{ label: "Дай практику", prompt: "Дай практическое задание по теме" }]
  };
}
