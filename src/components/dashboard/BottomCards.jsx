import { motion } from "framer-motion";
import { assets } from "../../assets";

export function BottomCards({ newsLiked, onToggleNewsLike, onOpenNews, onOpenProjects }) {
  return (
    <div className="bottom-cards">
      <motion.article
        className="glass-card news-card"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.24, duration: 0.36 }}
        onClick={onOpenNews}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            onOpenNews();
          }
        }}
      >
        <div className="news-image-wrap">
          <img src={assets.newsPhoto} alt="" />
        </div>
        <p className="news-text">
          Недавно яндекс провёл митап конференцию по фронтенду, а также бесплатные вебинары по javascript и typescript
        </p>
        <button
          className="news-like-btn"
          type="button"
          aria-label="Лайк новости"
          onClick={(event) => {
            event.stopPropagation();
            onToggleNewsLike();
          }}
        >
          <img src={newsLiked ? assets.heartFilledIcon : assets.heartOutlineIcon} alt="" />
        </button>
        <button className="news-link-btn" type="button" onClick={onOpenNews}>
          Подробнее
          <img src={assets.arrow16Icon} alt="" />
        </button>
      </motion.article>

      <motion.article
        className="glass-card projects-card"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.36 }}
        onClick={onOpenProjects}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            onOpenProjects();
          }
        }}
      >
        <div className="projects-head">
          <h2 className="projects-title">
            Актуальные проекты
            <img src={assets.sparklesIconA} alt="" className="title-spark" />
          </h2>
          <button className="small-arrow-btn" type="button">
            <img src={assets.alignCenterIcon} alt="" />
          </button>
        </div>
        <a className="project-link" href="#/projects/api-delivery">
          API для доставки еды
          <img src={assets.arrow15Icon} alt="" />
        </a>
        <div className="progress-track">
          <div className="progress-fill" />
        </div>
        <ul className="tasks-list">
          <li>
            <span className="task-dot" />
            <div>
              <strong>Завершить расчет LTV, ARPU и CAC</strong>
              <p>2 часа назад</p>
            </div>
          </li>
          <li className="task-muted">
            <span className="task-dot task-dot-muted" />
            <div>
              <strong>Завершить расчет LTV, ARPU и CAC</strong>
              <p>2 часа назад</p>
            </div>
          </li>
        </ul>
        <img src={assets.heartIllustration} alt="" className="project-side-art" />
      </motion.article>
    </div>
  );
}
