import { motion } from "framer-motion";
import { assets } from "../../assets";

const FALLBACK_HOME = {
  highlightCourse: {
    title: "Data Science + ML",
    imageUrl: "",
    path: "/courses/data-science-ml",
  },
  events: { count: 16, deltaLabel: "+2 за месяц" },
  productivity: { value: "80%", deltaLabel: "+60% за месяц" },
};

export function SummaryCards({
  home,
  isLoading = false,
  isError = false,
  useStaticFallback = true,
  onOpenCourses,
  onOpenCourseDetails,
  onOpenEvents
}) {
  if (isError && !useStaticFallback && home == null) {
    return (
      <div className="summary-grid summary-grid--error" aria-live="polite">
        <p className="api-inline-error">Не удалось загрузить блок «Для вас» и статистику. Проверьте сеть или backend.</p>
        <div className="glass-skeleton for-you-card" aria-hidden />
        <div className="glass-skeleton stats-card" aria-hidden />
        <div className="glass-skeleton stats-card productivity-card" aria-hidden />
      </div>
    );
  }

  const h = home ?? FALLBACK_HOME;
  const highlight = h.highlightCourse ?? FALLBACK_HOME.highlightCourse;
  const courseImageSrc = highlight.imageUrl?.trim() ? highlight.imageUrl : assets.courseImage;
  const courseTitle = highlight.title?.trim() || FALLBACK_HOME.highlightCourse.title;
  const eventsCount = h.events?.count ?? FALLBACK_HOME.events.count;
  const eventsDelta = h.events?.deltaLabel ?? FALLBACK_HOME.events.deltaLabel;
  const productivityValue = h.productivity?.value ?? FALLBACK_HOME.productivity.value;
  const productivityDelta = h.productivity?.deltaLabel ?? FALLBACK_HOME.productivity.deltaLabel;

  const showDemoBanner = isError && useStaticFallback;

  const handleOpenHighlight = () => {
    onOpenCourseDetails(highlight.path || FALLBACK_HOME.highlightCourse.path);
  };

  return (
    <div className="summary-grid" aria-busy={isLoading || undefined} style={{ opacity: isLoading ? 0.72 : 1 }}>
      {showDemoBanner ? (
        <p className="api-banner api-banner--warn" style={{ gridColumn: "1 / -1", margin: "0 0 8px" }} role="status">
          Данные панели недоступны — показаны демо-значения.
        </p>
      ) : null}
      <motion.article
        className="glass-card for-you-card"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.06, duration: 0.36 }}
      >
        <h2>Для вас</h2>
        <p>Подходящие курсы обучения</p>
        <button className="small-arrow-btn" onClick={onOpenCourses} type="button">
          <img src={assets.alignCenterIcon} alt="" />
        </button>
        <button className="for-you-course" type="button" onClick={handleOpenHighlight}>
          <img src={courseImageSrc} alt="" className="for-you-course-img" />
          <span className="for-you-course-pill">{courseTitle}</span>
          <img src={assets.group124Icon} alt="" className="for-you-course-arrow" />
        </button>
      </motion.article>

      <motion.article
        className="glass-card stats-card"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12, duration: 0.36 }}
        onClick={onOpenEvents}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            onOpenEvents();
          }
        }}
      >
        <h2>Мероприятия</h2>
        <p>Предстоящие в каталоге хакатонов</p>
        <button className="small-arrow-btn" type="button">
          <img src={assets.alignCenterIcon} alt="" />
        </button>
        <div className="events-info">
          <div>
            <strong>{eventsCount}</strong>
            <span>{eventsDelta}</span>
          </div>
          <div className="event-avatars">
            <span className="avatar-chip chip-gray">
              <img src={assets.gigachatLogo} alt="" />
            </span>
            <span className="avatar-chip chip-light">
              <img src={assets.cloudIcon} alt="" />
            </span>
            <span className="avatar-chip chip-white">
              <img src={assets.grokLogo} alt="" />
            </span>
          </div>
        </div>
      </motion.article>

      <motion.article
        className="glass-card stats-card productivity-card"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.18, duration: 0.36 }}
      >
        <h2>Продуктивность</h2>
        <p>Статистика за последний месяц</p>
        <div className="productivity-content">
          <div>
            <strong>{productivityValue}</strong>
            <span>{productivityDelta}</span>
          </div>
          <img src={assets.nodeJsIcon} alt="Node.js" />
        </div>
      </motion.article>
    </div>
  );
}
