import { motion } from "framer-motion";
import { assets } from "../../assets";
import { NewsMiniCard } from "../news/NewsMiniCard";

export function BottomCards({ newsItem, isNewsLiked, onToggleNewsLike, onOpenNews, onOpenProjects }) {
  return (
    <div className="bottom-cards">
      <NewsMiniCard
        item={newsItem}
        isLiked={isNewsLiked}
        onToggleLike={onToggleNewsLike}
        onOpen={onOpenNews}
        delay={0.24}
      />

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
        <a className="project-link" href="#/projects/api-food-delivery">
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
