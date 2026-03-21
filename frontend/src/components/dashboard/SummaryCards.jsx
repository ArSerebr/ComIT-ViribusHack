import { motion } from "framer-motion";
import { assets } from "../../assets";

export function SummaryCards({ onOpenCourses, onOpenCourseDetails, onOpenEvents }) {
  return (
    <div className="summary-grid">
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
        <button className="for-you-course" type="button" onClick={onOpenCourseDetails}>
          <img src={assets.courseImage} alt="" className="for-you-course-img" />
          <span className="for-you-course-pill">Data Science + ML</span>
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
        <p>Статистика за последний месяц</p>
        <button className="small-arrow-btn" type="button">
          <img src={assets.alignCenterIcon} alt="" />
        </button>
        <div className="events-info">
          <div>
            <strong>16</strong>
            <span>+2 за месяц</span>
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
            <strong>80%</strong>
            <span>+60% за месяц</span>
          </div>
          <img src={assets.nodeJsIcon} alt="Node.js" />
        </div>
      </motion.article>
    </div>
  );
}
