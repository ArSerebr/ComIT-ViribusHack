import { motion } from "framer-motion";
import { assets } from "../../assets";
import { LibraryArticleCard } from "./LibraryArticleCard";

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
    <button
      type="button"
      className={`library-preference-pill ${isSelected ? "library-preference-pill-selected" : ""}`}
      aria-pressed={isSelected}
      onClick={() => onToggle(option.id)}
    >
      {option.label}
    </button>
  );
}

export function LibraryPage({
  heroItem,
  showcaseItems,
  activeShowcaseIndex,
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
          <h2 className="library-hero-title">{heroItem.title}</h2>

          <div className="library-hero-updated">
            <TimeIcon />
            <span>{heroItem.updatedLabel}</span>
          </div>

          <button className="library-provider-pill" type="button">
            <ProviderIcon />
            <span>{heroItem.providerLabel}</span>
            <img src={assets.arrow16Icon} alt="" className="library-provider-chevron" />
          </button>

          <p className="library-hero-description">{heroItem.description}</p>
        </motion.section>

        <motion.section
          className="library-showcase"
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.34 }}
        >
          <div className="library-showcase-flower" aria-hidden="true">
            {Array.from({ length: 6 }).map((_, index) => (
              <span key={index} className={`library-showcase-petal library-showcase-petal-${index + 1}`} />
            ))}
          </div>

          <div className="glass-card library-showcase-card">
            <div className="library-showcase-brand">
              <ShowcaseBrandIcon />
              <span>{activeShowcaseItem.brandLabel}</span>
            </div>

            <div className="library-showcase-content">
              <div className="library-showcase-copy">
                <p>{activeShowcaseItem.eyebrow}</p>
                <h3>{activeShowcaseItem.title}</h3>
              </div>

              <div className="library-showcase-image-wrap">
                <img src={activeShowcaseItem.imageUrl} alt={activeShowcaseItem.title} className="library-showcase-image" />
              </div>
            </div>
          </div>

          <div className="library-showcase-controls">
            <button className="library-showcase-nav" type="button" aria-label="Предыдущий курс" onClick={onPrevShowcase}>
              <img src={assets.arrowSmallLeftIcon} alt="" />
            </button>
            <button className="library-showcase-nav library-showcase-nav-next" type="button" aria-label="Следующий курс" onClick={onNextShowcase}>
              <img src={assets.arrowSmallLeftIcon} alt="" />
            </button>
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
