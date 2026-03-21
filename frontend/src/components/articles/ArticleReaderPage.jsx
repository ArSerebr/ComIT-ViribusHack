import { motion } from "framer-motion";
import { assets } from "../../assets";

function DotMetaIcon({ className = "" }) {
  return <span className={`article-reader-meta-icon ${className}`.trim()} aria-hidden="true" />;
}

function RecommendationActionButton({ label, onClick }) {
  return (
    <button type="button" className="article-reader-reco-action" aria-label={label} onClick={onClick}>
      <span />
    </button>
  );
}

function RecommendationCard({ item, delay = 0, onOpen }) {
  return (
    <motion.article
      className={`glass-card article-reader-reco-card ${item.compact ? "article-reader-reco-card-compact" : ""}`.trim()}
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.28 }}
    >
      <button
        type="button"
        className="article-reader-reco-hit"
        aria-label={`Открыть материал ${item.title}`}
        onClick={() => onOpen(item)}
      />
      <img src={item.imageUrl} alt={item.title} className="article-reader-reco-image" />
      <div className="article-reader-reco-overlay" />
      <div className="article-reader-reco-copy">
        {item.badgeLabel ? <span className="article-reader-reco-badge">{item.badgeLabel}</span> : null}
        <strong>{item.title}</strong>
        <p>{item.subtitle}</p>
      </div>
      <div className="article-reader-reco-actions">
        <RecommendationActionButton label="Лайк" onClick={() => onOpen(item)} />
        <RecommendationActionButton label="Открыть ссылку" onClick={() => onOpen(item)} />
        <RecommendationActionButton label="Поделиться" onClick={() => onOpen(item)} />
      </div>
    </motion.article>
  );
}

function ArticleMode({ article, recommendations, onOpenRecommendation, onOpenRelatedCourse }) {
  return (
    <div className="article-reader-layout">
      <motion.section
        className="article-reader-main"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="article-reader-title">{article.title}</h2>
        <div className="article-reader-meta-row">
          <span className="article-reader-meta-item">
            <DotMetaIcon className="article-reader-meta-icon-time" />
            {article.updatedLabel}
          </span>
          <span className="article-reader-meta-item">
            <DotMetaIcon className="article-reader-meta-icon-view" />
            {article.viewsLabel}
          </span>
        </div>

        <article className="glass-card article-reader-main-card">
          {article.paragraphs.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}

          <figure className="article-reader-illustration">
            <img src={article.heroImageUrl} alt="Иллюстрация к статье" />
          </figure>

          <h3>Кратко, о чем поговорим:</h3>
          <ol>
            {article.points.map((point) => (
              <li key={point}>{point}</li>
            ))}
          </ol>
        </article>

        <button type="button" className="news-link-btn article-reader-related-btn" onClick={onOpenRelatedCourse}>
          <span className="news-link-label">Открыть связанный курс</span>
          <span className="news-link-arrow-wrap">
            <img src={assets.arrow16Icon} alt="" />
          </span>
          <span className="news-link-btn-shine" />
        </button>
      </motion.section>

      <aside className="article-reader-sidebar">
        {recommendations.map((item, index) => (
          <RecommendationCard key={item.id} item={item} delay={0.08 + index * 0.06} onOpen={onOpenRecommendation} />
        ))}
      </aside>
    </div>
  );
}

function CourseMode({ course }) {
  return (
    <div className="article-course-layout">
      <motion.section
        className="article-course-copy"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="article-course-tags">
          {course.categoryLabels.map((label) => (
            <span key={label} className="article-course-tag">
              {label}
            </span>
          ))}
        </div>

        <h2>{course.title}</h2>
        <p className="article-course-summary">{course.summary}</p>

        <ul>
          {course.outcomes.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>

        <button type="button" className="projects-hub-create-btn article-course-cta">
          <span>{course.ctaLabel}</span>
          <img src={assets.arrow16Icon} alt="" />
        </button>
      </motion.section>

      <motion.article
        className="glass-card article-course-provider"
        initial={{ opacity: 0, x: 18 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.32, delay: 0.06 }}
      >
        <div className="article-course-provider-brand">
          <span className="article-course-provider-brand-icon" aria-hidden="true" />
          <span>{course.providerName}</span>
        </div>
        <div className="article-course-provider-copy">
          <p>{course.providerTrack}</p>
          <h3>{course.providerTitle}</h3>
        </div>
        <div className="article-course-provider-image-wrap">
          <img src={course.providerImageUrl} alt={course.providerTitle} />
        </div>
      </motion.article>
    </div>
  );
}

export function ArticleReaderPage({
  mode = "article",
  article,
  course,
  recommendations = [],
  onBack,
  onOpenRecommendation,
  onOpenRelatedCourse
}) {
  return (
    <section className="article-reader-page">
      <div className="library-page-head article-reader-head">
        <button className="news-back-btn library-back-btn" type="button" aria-label="Назад" onClick={onBack}>
          <img src={assets.arrowSmallLeftIcon} alt="" />
        </button>
        <h1 className="library-page-title">Статьи и курсы</h1>
      </div>

      {mode === "course" && course ? (
        <CourseMode course={course} />
      ) : (
        <ArticleMode
          article={article}
          recommendations={recommendations}
          onOpenRecommendation={onOpenRecommendation}
          onOpenRelatedCourse={onOpenRelatedCourse}
        />
      )}
    </section>
  );
}
