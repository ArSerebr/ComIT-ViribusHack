import { motion } from "framer-motion";
import { assets } from "../../assets";

function DetailCard({ children, className = "", delay = 0 }) {
  return (
    <motion.article
      className={`glass-card project-details-card ${className}`.trim()}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.32 }}
    >
      {children}
    </motion.article>
  );
}

function SectionTitle({ title, caption, iconClass, decoration }) {
  return (
    <div className="project-details-card-head">
      <div>
        <h2 className="project-details-card-title">
          {title}
          <span className={`project-details-title-icon ${iconClass}`} aria-hidden="true" />
          {decoration}
        </h2>
        {caption ? <p className="project-details-card-caption">{caption}</p> : null}
      </div>
    </div>
  );
}

function IntegrationBrand({ brand }) {
  if (brand === "github") {
    return (
      <div className="project-details-brand project-details-brand-github">
        <span className="project-details-github-mark" aria-hidden="true">
          <span className="project-details-github-face" />
        </span>
        <span className="project-details-brand-label">GitHub</span>
      </div>
    );
  }

  return (
    <div className="project-details-brand project-details-brand-timeweb">
      <span className="project-details-timeweb-wordmark">
        timeweb
        <span className="project-details-timeweb-chevron" aria-hidden="true" />
      </span>
    </div>
  );
}

export function ProjectDetailsPage({ project, onBack, onJoinProject }) {
  return (
    <section className="project-details-page">
      <div className="project-details-head">
        <div className="project-details-heading">
          <button className="news-back-btn project-details-back-btn" type="button" aria-label="Назад к проектам" onClick={onBack}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>

          <div className="project-details-title-block">
            <h1 className="project-details-title">{project.title}</h1>
            <p className="project-details-byline">
              By <span>{project.ownerName}</span>
            </p>
          </div>
        </div>

        <button className="projects-hub-create-btn project-details-join-btn" type="button" onClick={() => onJoinProject(project)}>
          <img src={assets.plusSmallIcon} alt="" />
          <span>{project.joinLabel}</span>
        </button>
      </div>

      <div className="project-details-grid">
        <div className="project-details-side-grid">
          <DetailCard className="project-details-team-card" delay={0.06}>
            <SectionTitle title="Команда" caption={project.teamCaption} iconClass="project-details-title-icon-team" />

            <div className="project-details-team-footer">
              <div className="project-details-avatar-stack" aria-label="Участники проекта">
                {project.teamMembersPreview.map((member) => (
                  <span
                    key={member.id}
                    className={`project-details-avatar-stack-item project-details-avatar-stack-item-${member.avatarVariant}`}
                  >
                    <img src={member.avatarUrl} alt={member.name} className="project-details-avatar-stack-image" />
                  </span>
                ))}
              </div>

              <button className="project-details-team-action" type="button">
                Посмотреть всех
              </button>
            </div>
          </DetailCard>

          <DetailCard className="project-details-productivity-card" delay={0.12}>
            <SectionTitle title="Продуктивность" caption={project.productivityCaption} iconClass="project-details-title-icon-productivity" />

            <div className="project-details-metric-block">
              <strong>{project.productivity.value}</strong>
              <span>{project.productivity.delta}</span>
            </div>

            <img src={assets.heartIllustration} alt="" className="project-details-fluff project-details-fluff-productivity" />
          </DetailCard>

          <DetailCard className="project-details-progress-card" delay={0.18}>
            <SectionTitle title="Прогресс" caption={project.progressCaption} iconClass="project-details-title-icon-progress" />

            <div className="project-details-metric-block project-details-progress-value">
              <strong>{project.progress.value}</strong>
            </div>

            <div className="project-details-progress-track" aria-label={`Готовность ${project.progress.value}`}>
              <div className="project-details-progress-fill" style={{ width: `${project.progress.percent}%` }} />
            </div>
          </DetailCard>

          <DetailCard className="project-details-todo-card" delay={0.24}>
            <SectionTitle
              title="To-Do"
              caption={project.todoCaption}
              iconClass="project-details-title-icon-empty"
              decoration={<img src={assets.sparklesIconA} alt="" className="project-details-todo-spark" />}
            />

            <div className="project-details-todo-item">
              <span className="project-details-todo-dot" aria-hidden="true" />
              <div className="project-details-todo-copy">
                <strong>{project.todo.task}</strong>
                <p>{project.todo.updatedLabel}</p>
              </div>
            </div>

            <button className="project-hub-card-open project-details-todo-open" type="button" aria-label="Открыть задачи">
              <span className="project-hub-card-open-arrow" aria-hidden="true" />
            </button>

            <img src={assets.heartIllustration} alt="" className="project-details-fluff project-details-fluff-todo" />
          </DetailCard>
        </div>

        <DetailCard className="project-details-integrations-card" delay={0.14}>
          <div className="project-details-card-topline">
            <span className="project-hub-card-code project-hub-card-code-idea">
              <span className="project-hub-card-dot project-hub-card-dot-idea" />
              {project.code}
            </span>
          </div>

          <div className="project-details-integrations-head">
            <h2 className="project-details-integrations-title">
              Интеграции с другими сервисами
              <span className="project-details-integrations-title-icon" aria-hidden="true" />
            </h2>
            <p>{project.integrationCaption}</p>
          </div>

          <div className="project-details-integrations-list">
            {project.integrations.map((integration) => (
              <div key={integration.id} className="project-details-integration-row">
                <IntegrationBrand brand={integration.brand} />

                <p className="project-details-integration-description">{integration.description}</p>

                <div className="project-details-integration-status">
                  <strong>
                    <span className="project-details-integration-status-dot" aria-hidden="true" />
                    {integration.statusLabel}
                  </strong>
                  <span>{integration.connectedSince}</span>
                </div>

                <button className="project-details-integration-open" type="button" aria-label={`Открыть интеграцию ${integration.brand}`}>
                  <span className="project-details-integration-open-arrow" aria-hidden="true" />
                </button>
              </div>
            ))}
          </div>
        </DetailCard>
      </div>

      <motion.section
        className="glass-card project-details-members-card"
        initial={{ opacity: 0, y: 28 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.22, duration: 0.34 }}
      >
        <header className="project-details-members-head">
          <h2>
            Все участники проекта
            <span className="project-details-title-icon project-details-title-icon-members" aria-hidden="true" />
          </h2>
        </header>

        <div className="project-details-members-table-wrap">
          <table className="project-details-members-table">
            <thead>
              <tr>
                <th>ComIT ID</th>
                <th>Профиль</th>
                <th>Время в проекте</th>
                <th>Должность</th>
                <th>Статус</th>
                <th>Последние задачи</th>
              </tr>
            </thead>

            <tbody>
              {project.participants.map((member) => (
                <tr key={member.id}>
                  <td>{member.comitId}</td>
                  <td>
                    <div className="project-details-member">
                      <span className={`project-details-member-avatar project-details-member-avatar-${member.avatarVariant}`}>
                        <img src={member.avatarUrl} alt={member.name} />
                      </span>
                      <span className="project-details-member-name">{member.name}</span>
                    </div>
                  </td>
                  <td>{member.timeInProject}</td>
                  <td>{member.role}</td>
                  <td>
                    <span className="project-details-status-pill">
                      <span className="project-details-status-dot" aria-hidden="true" />
                      {member.status}
                    </span>
                  </td>
                  <td>{member.lastTask}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.section>
    </section>
  );
}
