import { AnimatePresence, motion } from "framer-motion";
import { assets } from "../../assets";
import { LibraryArticleCard } from "./LibraryArticleCard";

const SHOWCASE_TRANSITION = {
  type: "spring",
  stiffness: 320,
  damping: 30,
  mass: 0.92
};

const SHOWCASE_PANEL_VARIANTS = {
  enter: (direction) => ({
    opacity: 0,
    x: direction > 0 ? 56 : -56,
    y: 18,
    rotate: direction > 0 ? 2.4 : -2.4,
    scale: 0.96,
    filter: "blur(12px)"
  }),
  center: {
    opacity: 1,
    x: 0,
    y: 0,
    rotate: 0,
    scale: 1,
    filter: "blur(0px)"
  },
  exit: (direction) => ({
    opacity: 0,
    x: direction > 0 ? -44 : 44,
    y: -14,
    rotate: direction > 0 ? -1.8 : 1.8,
    scale: 0.985,
    filter: "blur(8px)"
  })
};

const SHOWCASE_COPY_VARIANTS = {
  enter: (direction) => ({
    opacity: 0,
    x: direction > 0 ? -42 : 42,
    y: 18,
    filter: "blur(10px)"
  }),
  center: {
    opacity: 1,
    x: 0,
    y: 0,
    filter: "blur(0px)"
  },
  exit: (direction) => ({
    opacity: 0,
    x: direction > 0 ? 30 : -30,
    y: -12,
    filter: "blur(8px)"
  })
};

const SHOWCASE_STAGGER_VARIANTS = {
  enter: {},
  center: {
    transition: {
      staggerChildren: 0.07,
      delayChildren: 0.06
    }
  },
  exit: {
    transition: {
      staggerChildren: 0.04,
      staggerDirection: -1
    }
  }
};

const SHOWCASE_ITEM_VARIANTS = {
  enter: {
    opacity: 0,
    y: 20,
    filter: "blur(8px)"
  },
  center: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: {
      duration: 0.28,
      ease: [0.22, 1, 0.36, 1]
    }
  },
  exit: {
    opacity: 0,
    y: -14,
    filter: "blur(6px)",
    transition: {
      duration: 0.18,
      ease: [0.4, 0, 1, 1]
    }
  }
};

const SHOWCASE_IMAGE_VARIANTS = {
  enter: (direction) => ({
    opacity: 0,
    x: direction > 0 ? 86 : -86,
    y: 20,
    rotate: direction > 0 ? 8 : -8,
    scale: 0.88,
    filter: "blur(14px)"
  }),
  center: {
    opacity: 1,
    x: 0,
    y: 0,
    rotate: 0,
    scale: 1,
    filter: "blur(0px)",
    transition: {
      ...SHOWCASE_TRANSITION,
      delay: 0.08
    }
  },
  exit: (direction) => ({
    opacity: 0,
    x: direction > 0 ? -74 : 74,
    y: -18,
    rotate: direction > 0 ? -6 : 6,
    scale: 0.92,
    filter: "blur(12px)",
    transition: {
      duration: 0.2,
      ease: [0.4, 0, 1, 1]
    }
  })
};

function TimeIcon() {
  return <span className="library-time-icon" aria-hidden="true" />;
}

function ProviderIcon() {
  return <span className="library-provider-icon" aria-hidden="true" />;
}

function ShowcaseBrandIcon() {
  return <span className="library-showcase-brand-icon" aria-hidden="true" />;
}

function PreferenceButton({ option, isSelected, onToggle }) {
  return (
    <motion.button
      type="button"
      className={`library-preference-pill ${isSelected ? "library-preference-pill-selected" : ""}`}
      aria-pressed={isSelected}
      onClick={() => onToggle(option.id)}
      whileHover={{ y: -3, scale: 1.02 }}
      whileTap={{ scale: 0.96 }}
      animate={isSelected ? { y: [0, -2, 0], scale: [1, 1.03, 1] } : { y: 0, scale: 1 }}
      transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
    >
      <AnimatePresence initial={false}>
        {isSelected ? (
          <motion.span
            key="preference-glow"
            className="library-preference-pill-glow"
            initial={{ opacity: 0, scale: 0.72 }}
            animate={{ opacity: [0, 0.95, 0.78], scale: [0.72, 1.06, 1] }}
            exit={{ opacity: 0, scale: 1.08 }}
            transition={{ duration: 0.34, ease: [0.22, 1, 0.36, 1] }}
          />
        ) : null}
      </AnimatePresence>
      <motion.span
        className="library-preference-pill-label"
        animate={isSelected ? { letterSpacing: ["0em", "0.01em", "0em"] } : { letterSpacing: "0em" }}
        transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
      >
        {option.label}
      </motion.span>
    </motion.button>
  );
}

export function LibraryPage({
  heroItem,
  showcaseItems,
  activeShowcaseIndex,
  showcaseDirection = 1,
  interestOptions,
  selectedInterests,
  articleItems,
  onBack,
  onPrevShowcase,
  onNextShowcase,
  onToggleInterest,
  onSaveInterests
}) {
  const activeShowcaseItem = showcaseItems[activeShowcaseIndex] || showcaseItems[0];
  const activeHeroItem = activeShowcaseItem?.hero || heroItem;

  return (
    <section className="library-page">
      <div className="library-page-head">
        <button className="news-back-btn library-back-btn" type="button" aria-label="Назад на главную" onClick={onBack}>
          <img src={assets.arrowSmallLeftIcon} alt="" />
        </button>
        <h1 className="library-page-title">Статьи и курсы</h1>
      </div>

      <div className="library-top-layout">
        <motion.section
          className="library-hero-copy"
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.04, duration: 0.32 }}
        >
          <AnimatePresence mode="wait" initial={false} custom={showcaseDirection}>
            <motion.div
              key={activeShowcaseItem.id}
              className="library-hero-stage"
              custom={showcaseDirection}
              variants={SHOWCASE_COPY_VARIANTS}
              initial="enter"
              animate="center"
              exit="exit"
              transition={SHOWCASE_TRANSITION}
            >
              <motion.h2 className="library-hero-title" variants={SHOWCASE_ITEM_VARIANTS}>
                {activeHeroItem.title}
              </motion.h2>

              <motion.div className="library-hero-updated" variants={SHOWCASE_ITEM_VARIANTS}>
                <TimeIcon />
                <span>{activeHeroItem.updatedLabel}</span>
              </motion.div>

              <motion.button className="library-provider-pill" type="button" variants={SHOWCASE_ITEM_VARIANTS}>
                <ProviderIcon />
                <span>{activeHeroItem.providerLabel}</span>
                <img src={assets.arrow16Icon} alt="" className="library-provider-chevron" />
              </motion.button>

              <motion.p className="library-hero-description" variants={SHOWCASE_ITEM_VARIANTS}>
                {activeHeroItem.description}
              </motion.p>
            </motion.div>
          </AnimatePresence>
        </motion.section>

        <motion.section
          className="library-showcase"
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.34 }}
        >
          <div className="library-showcase-flower-shell" aria-hidden="true">
            <motion.div
              className="library-showcase-flower"
              animate={{
                rotate: showcaseDirection * 12,
                scale: [0.985, 1.02, 0.985],
                y: [0, -10, 0]
              }}
              transition={{
                rotate: SHOWCASE_TRANSITION,
                scale: { duration: 6.4, repeat: Infinity, ease: "easeInOut" },
                y: { duration: 6.4, repeat: Infinity, ease: "easeInOut" }
              }}
            >
              {Array.from({ length: 6 }).map((_, index) => (
                <span key={index} className={`library-showcase-petal library-showcase-petal-${index + 1}`} />
              ))}
            </motion.div>
          </div>

          <motion.div
            className="glass-card library-showcase-card"
            animate={{
              boxShadow: [
                "0 26px 62px rgba(0, 0, 0, 0.3), inset 0 0 12px 1px rgba(255, 255, 255, 0.128)",
                "0 30px 74px rgba(27, 56, 128, 0.34), inset 0 0 12px 1px rgba(255, 255, 255, 0.148)",
                "0 26px 62px rgba(0, 0, 0, 0.3), inset 0 0 12px 1px rgba(255, 255, 255, 0.128)"
              ]
            }}
            transition={{ duration: 5.6, repeat: Infinity, ease: "easeInOut" }}
          >
            <AnimatePresence mode="wait" initial={false} custom={showcaseDirection}>
              <motion.div
                key={activeShowcaseItem.id}
                className="library-showcase-card-stage"
                custom={showcaseDirection}
                variants={SHOWCASE_PANEL_VARIANTS}
                initial="enter"
                animate="center"
                exit="exit"
                transition={SHOWCASE_TRANSITION}
              >
                <motion.div className="library-showcase-brand" variants={SHOWCASE_ITEM_VARIANTS}>
                  <ShowcaseBrandIcon />
                  <span>{activeShowcaseItem.brandLabel}</span>
                </motion.div>

                <motion.div
                  className="library-showcase-content"
                  variants={SHOWCASE_STAGGER_VARIANTS}
                  initial="enter"
                  animate="center"
                  exit="exit"
                >
                  <motion.div className="library-showcase-copy" variants={SHOWCASE_ITEM_VARIANTS}>
                    <p>{activeShowcaseItem.eyebrow}</p>
                    <h3>{activeShowcaseItem.title}</h3>
                  </motion.div>

                  <motion.div className="library-showcase-image-wrap" custom={showcaseDirection} variants={SHOWCASE_IMAGE_VARIANTS}>
                    <img src={activeShowcaseItem.imageUrl} alt={activeShowcaseItem.title} className="library-showcase-image" />
                  </motion.div>
                </motion.div>
              </motion.div>
            </AnimatePresence>
          </motion.div>

          <div className="library-showcase-controls">
            <motion.button
              className="library-showcase-nav"
              type="button"
              aria-label="Предыдущий курс"
              onClick={onPrevShowcase}
              whileHover={{ y: -3, scale: 1.04 }}
              whileTap={{ y: 0, scale: 0.95 }}
            >
              <img src={assets.arrowSmallLeftIcon} alt="" />
            </motion.button>
            <motion.button
              className="library-showcase-nav library-showcase-nav-next"
              type="button"
              aria-label="Следующий курс"
              onClick={onNextShowcase}
              whileHover={{ y: -3, scale: 1.04 }}
              whileTap={{ y: 0, scale: 0.95 }}
            >
              <img src={assets.arrowSmallLeftIcon} alt="" />
            </motion.button>
          </div>
        </motion.section>

        <motion.aside
          className="glass-card library-preferences-card"
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.14, duration: 0.34 }}
        >
          <h2>Настрой свою ленту</h2>
          <p>Выбери темы и интересы для лучших рекомендаций</p>

          <div className="library-preferences-grid">
            {interestOptions.map((option) => (
              <PreferenceButton
                key={option.id}
                option={option}
                isSelected={Boolean(selectedInterests[option.id])}
                onToggle={onToggleInterest}
              />
            ))}
          </div>

          <button className="library-save-btn" type="button" onClick={onSaveInterests}>
            Сохранить интересы
          </button>
        </motion.aside>
      </div>

      <div className="library-articles-grid">
        {articleItems.map((item, index) => (
          <LibraryArticleCard key={item.id} item={item} delay={0.18 + index * 0.06} />
        ))}
      </div>
    </section>
  );
}
