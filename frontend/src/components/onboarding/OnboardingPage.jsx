import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { assets } from "../../assets";

const STEPS = [
  {
    id: "interests",
    title: "Что вас сейчас больше всего интересует?",
    type: "multi",
    options: [
      { id: "ux-ui-design", label: "UX/UI Design" },
      { id: "ai-ml", label: "AI / ML" },
      { id: "backend", label: "Backend" },
      { id: "frontend", label: "Frontend" },
      { id: "data-science", label: "Data Science" },
      { id: "devops", label: "DevOps" },
      { id: "mobile", label: "Mobile" },
      { id: "gamedev", label: "GameDev" },
      { id: "security", label: "Security" },
    ],
  },
  {
    id: "goal",
    title: "Какая ваша основная цель?",
    type: "single",
    options: [
      { id: "learn", label: "Освоить новые навыки" },
      { id: "team", label: "Найти команду" },
      { id: "project", label: "Создать свой проект" },
    ],
  },
  {
    id: "level",
    title: "Как вы оцениваете свой уровень?",
    type: "single",
    options: [
      { id: "beginner", label: "Новичок" },
      { id: "product-team", label: "Работал в продуктовых командах" },
      { id: "some-projects", label: "Делал пару проектов" },
    ],
  },
  {
    id: "skills",
    title: "Какие у вас есть навыки?",
    type: "multi",
    options: [
      { id: "figma-ux", label: "Figma + UX/UI" },
      { id: "react", label: "React" },
      { id: "angular", label: "Angular" },
      { id: "tailwind", label: "Tailwind CSS" },
      { id: "rest-api", label: "REST API" },
      { id: "webpack", label: "Webpack" },
    ],
  },
  {
    id: "source",
    title: "Откуда вы про нас узнали?",
    type: "single",
    options: [
      { id: "youtube", label: "YouTube" },
      { id: "telegram", label: "Telegram" },
      { id: "yandex", label: "Yandex" },
      { id: "university", label: "В университете" },
      { id: "vk", label: "VK" },
      { id: "friends", label: "От друзей" },
    ],
  },
];

const CARD_VARIANTS = {
  enter: (direction) => ({
    opacity: 0,
    x: direction > 0 ? 48 : -48,
    scale: 0.97,
    filter: "blur(8px)",
  }),
  center: {
    opacity: 1,
    x: 0,
    scale: 1,
    filter: "blur(0px)",
  },
  exit: (direction) => ({
    opacity: 0,
    x: direction > 0 ? -48 : 48,
    scale: 0.97,
    filter: "blur(8px)",
  }),
};

const CARD_TRANSITION = {
  type: "spring",
  stiffness: 360,
  damping: 32,
  mass: 0.88,
};

const OPTION_VARIANTS = {
  hidden: { opacity: 0, y: 10, scale: 0.95 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { delay: i * 0.045, type: "spring", stiffness: 380, damping: 28 },
  }),
};

export function OnboardingPage({ isSubmitting = false, onComplete }) {
  const [stepIndex, setStepIndex] = useState(0);
  const [direction, setDirection] = useState(1);
  const [answers, setAnswers] = useState({
    interests: [],
    goal: null,
    level: null,
    skills: [],
    source: null,
  });

  const step = STEPS[stepIndex];
  const isLastStep = stepIndex === STEPS.length - 1;
  const progress = (stepIndex + 1) / STEPS.length;

  const getSelected = (stepId) => {
    const val = answers[stepId];
    if (Array.isArray(val)) return val;
    return val ? [val] : [];
  };

  const toggleOption = (stepId, optionId, type) => {
    setAnswers((prev) => {
      if (type === "single") {
        return { ...prev, [stepId]: optionId };
      }
      const current = prev[stepId] || [];
      const exists = current.includes(optionId);
      return {
        ...prev,
        [stepId]: exists ? current.filter((id) => id !== optionId) : [...current, optionId],
      };
    });
  };

  const canProceed = () => {
    const val = answers[step.id];
    if (step.type === "single") return val != null;
    return Array.isArray(val) && val.length > 0;
  };

  const handleNext = () => {
    if (!canProceed()) return;
    if (isLastStep) {
      onComplete(answers);
      return;
    }
    setDirection(1);
    setStepIndex((prev) => prev + 1);
  };

  const continueLabel = isLastStep ? "Перейти на главный экран" : "Продолжить";
  const selected = getSelected(step.id);

  return (
    <section className="onboarding-page">
      {/* Animated background shapes */}
      <motion.img
        className="bg-shape bg-shape-top"
        src={assets.backgroundShape}
        alt=""
        animate={{ x: [0, 28, 0], y: [0, -18, 0], rotate: [4.07, 6.3, 4.07] }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.img
        className="bg-shape bg-shape-bottom"
        src={assets.backgroundShape}
        alt=""
        animate={{ x: [0, -34, 0], y: [0, 24, 0], rotate: [156, 152, 156] }}
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Logo */}
      <motion.div
        className="onboarding-logo"
        initial={{ opacity: 0, y: -14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.32 }}
      >
        <img src={assets.untitledLogo} alt="" />
        <strong>ComIT</strong>
      </motion.div>

      {/* Step card */}
      <div className="onboarding-stage">
        <AnimatePresence mode="wait" custom={direction}>
          <motion.div
            key={stepIndex}
            className="onboarding-card glass-card"
            custom={direction}
            variants={CARD_VARIANTS}
            initial="enter"
            animate="center"
            exit="exit"
            transition={CARD_TRANSITION}
          >
            <h2 className="onboarding-question">{step.title}</h2>

            <motion.div
              className="onboarding-options"
              initial="hidden"
              animate="visible"
            >
              {step.options.map((option, i) => {
                const isActive = selected.includes(option.id);
                return (
                  <motion.button
                    key={option.id}
                    type="button"
                    className={`onboarding-option${isActive ? " onboarding-option-active" : ""}`}
                    custom={i}
                    variants={OPTION_VARIANTS}
                    whileHover={{ scale: 1.04, y: -2 }}
                    whileTap={{ scale: 0.96 }}
                    onClick={() => toggleOption(step.id, option.id, step.type)}
                  >
                    {option.label}
                  </motion.button>
                );
              })}
            </motion.div>

            <motion.button
              type="button"
              className={`onboarding-continue${!canProceed() ? " onboarding-continue-disabled" : ""}`}
              disabled={!canProceed() || isSubmitting}
              onClick={handleNext}
              whileHover={canProceed() ? { scale: 1.03, y: -1 } : {}}
              whileTap={canProceed() ? { scale: 0.97 } : {}}
            >
              {isSubmitting && isLastStep ? "Сохраняем…" : continueLabel}
            </motion.button>

            {/* Progress bar */}
            <div className="onboarding-progress-wrap">
              <motion.div
                className="onboarding-progress-bar"
                initial={{ width: `${((stepIndex) / STEPS.length) * 100}%` }}
                animate={{ width: `${progress * 100}%` }}
                transition={{ type: "spring", stiffness: 280, damping: 26 }}
              />
            </div>

            <span className="onboarding-step-label">{stepIndex + 1}/{STEPS.length}</span>
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  );
}
