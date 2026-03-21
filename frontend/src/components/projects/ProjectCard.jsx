import { motion } from "framer-motion";

function LockIcon() {
  return <span className="project-hub-lock-icon" aria-hidden="true" />;
}

function UpdateIcon() {
  return <span className="project-hub-update-icon" aria-hidden="true" />;
}

function formatVisibility(visibility) {
  if (visibility === "private") {
    return "Приватный";
  }
  if (visibility === "public") {
    return "Публичный";
  }
  return "";
}

export function ProjectCard({ project, tone, delay = 0, onOpenProject }) {
  const visibilityLabel = formatVisibility(project.visibility);

  return (
    <motion.article
      className={`glass-card project-hub-card project-hub-card-${tone}`}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.32 }}
    >
      <div className="project-hub-card-top">
        <span className={`project-hub-card-code project-hub-card-code-${tone}`}>
          <span className={`project-hub-card-dot project-hub-card-dot-${tone}`} />
          {project.code}
        </span>

        {visibilityLabel ? (
          <span className="project-hub-card-visibility">
            <LockIcon />
            {visibilityLabel}
          </span>
        ) : null}
      </div>

      <h3 className="project-hub-card-title">
        {project.title}
        {project.isHot ? <span className="project-hub-card-fire">{"\uD83D\uDD25"}</span> : null}
      </h3>

      <p className="project-hub-card-description">{project.description}</p>

      <div className="project-hub-card-team">
        <img src={project.teamAvatarUrl} alt="" className="project-hub-card-avatar" />
        <span className="project-hub-card-team-name">{project.teamName}</span>
      </div>

      <div className="project-hub-card-footer">
        <div className="project-hub-card-updated">
          <UpdateIcon />
          <span>{project.updatedLabel}</span>
        </div>

        <button
          className="project-hub-card-open"
          type="button"
          aria-label={`Открыть проект ${project.title}`}
          onClick={() => onOpenProject(project)}
        >
          <span className="project-hub-card-open-arrow" aria-hidden="true" />
        </button>
      </div>
    </motion.article>
  );
}

