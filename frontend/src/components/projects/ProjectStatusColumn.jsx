import { ProjectCard } from "./ProjectCard";

export function ProjectStatusColumn({ column, columnIndex, onOpenProject }) {
  return (
    <section className={`projects-hub-column projects-hub-column-${column.id}`}>
      <header className={`projects-hub-column-head projects-hub-column-head-${column.id}`}>
        <h2>
          {column.title} ({column.count})
        </h2>
      </header>

      <div className="projects-hub-card-list">
        {column.projects.map((project, projectIndex) => (
          <ProjectCard
            key={project.id}
            project={project}
            tone={column.id}
            delay={0.08 + columnIndex * 0.08 + projectIndex * 0.05}
            onOpenProject={onOpenProject}
          />
        ))}
      </div>
    </section>
  );
}
