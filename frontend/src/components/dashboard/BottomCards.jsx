import { motion } from "framer-motion";
import { assets } from "../../assets";
import { NewsMiniCard } from "../news/NewsMiniCard";

const FALLBACK_PROJECT = {
  title: "API для доставки еды",
  detailsUrl: "/projects/api-food-delivery",
  updatedLabel: "Недавняя активность",
};

export function BottomCards({
  newsItem,
  projectHighlight,
  isNewsLiked,
  onToggleNewsLike,
  onOpenNews,
  onOpenProjects,
  onOpenProjectLink,
  isNewsLoading = false,
  isNewsError = false,
  useStaticFallback = true
}) {
  const project = projectHighlight ?? FALLBACK_PROJECT;
  const projectHash = project.detailsUrl?.startsWith("/") ? `#${project.detailsUrl}` : `#/projects`;

  const handleProjectNavigate = (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (onOpenProjectLink) {
      onOpenProjectLink(project);
      return;
    }
    if (project.detailsUrl) {
      window.location.hash = project.detailsUrl.startsWith("/") ? project.detailsUrl : `/${project.detailsUrl}`;
    }
  };

  const showNewsSkeleton = isNewsLoading || (!newsItem && (isNewsError || !useStaticFallback));

  return (
    <div className="bottom-cards">
      {showNewsSkeleton ? (
        <div className="glass-card news-card news-card-skeleton" aria-busy="true" aria-label="Загрузка новостей">
          <div className="news-skeleton-image glass-skeleton" />
          <div className="news-skeleton-text glass-skeleton" />
        </div>
      ) : (
        <NewsMiniCard
          item={newsItem}
          isLiked={isNewsLiked}
          onToggleLike={onToggleNewsLike}
          onOpen={onOpenNews}
          delay={0.24}
        />
      )}

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
        <a className="project-link" href={projectHash} onClick={handleProjectNavigate}>
          {project.title}
          <img src={assets.arrow15Icon} alt="" />
        </a>
        <div className="progress-track">
          <div className="progress-fill" />
        </div>
        <ul className="tasks-list">
          <li>
            <span className="task-dot" />
            <div>
              <strong>Последнее обновление</strong>
              <p>{project.updatedLabel}</p>
            </div>
          </li>
          <li className="task-muted">
            <span className="task-dot task-dot-muted" />
            <div>
              <strong>Откройте хаб проектов</strong>
              <p>чтобы увидеть все команды</p>
            </div>
          </li>
        </ul>
        <img src={assets.heartIllustration} alt="" className="project-side-art" />
      </motion.article>
    </div>
  );
}
