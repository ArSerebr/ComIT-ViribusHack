import { useState } from "react";
import { motion } from "framer-motion";
import { assets } from "../../assets";
import { ProjectStatusColumn } from "./ProjectStatusColumn";

export function ProjectHubPage({
  columns,
  onBack,
  onCreateProject,
  onOpenProject,
  isLoading = false,
  isError = false,
  useStaticFallback = true
}) {
  const [activeColumnIndex, setActiveColumnIndex] = useState(0);
  const showSkeleton = isLoading && !columns?.length;
  const showEmpty = !showSkeleton && !columns?.length && isError && !useStaticFallback;

  return (
    <section className="projects-hub-page">
      <div className="projects-hub-head">
        <div className="projects-hub-title-wrap">
          <button className="news-back-btn projects-hub-back-btn" type="button" aria-label="Назад на главную" onClick={onBack}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <h1 className="projects-hub-title">
            <span className="projects-hub-title-full">Проекты университета</span>
            <span className="projects-hub-title-short">Проекты</span>
          </h1>
        </div>

        <div className="projects-hub-head-actions">
          <motion.button
            className="projects-hub-create-btn"
            type="button"
            initial={{ opacity: 0, x: 18 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.12, duration: 0.3 }}
            onClick={onCreateProject}
          >
            <img src={assets.plusSmallIcon} alt="" />
            <span>Создать проект</span>
          </motion.button>

        </div>
      </div>

      {!showSkeleton && !showEmpty && columns.length > 0 ? (
        <div className="projects-hub-column-tabs">
          {columns.map((column, index) => (
            <button
              key={column.id}
              type="button"
              className={`projects-hub-column-tab ${activeColumnIndex === index ? "projects-hub-column-tab-active" : ""}`}
              onClick={() => setActiveColumnIndex(index)}
            >
              {column.title}
              <span className="projects-hub-column-tab-count">{column.count}</span>
            </button>
          ))}
        </div>
      ) : null}

      <div className="projects-hub-columns">
        {showSkeleton ? (
          <>
            <div className="glass-skeleton" style={{ minHeight: 320, borderRadius: "var(--radius-card)" }} aria-hidden />
            <div className="glass-skeleton" style={{ minHeight: 320, borderRadius: "var(--radius-card)" }} aria-hidden />
            <div className="glass-skeleton" style={{ minHeight: 320, borderRadius: "var(--radius-card)" }} aria-hidden />
          </>
        ) : null}
        {showEmpty ? (
          <p className="projects-hub-empty" role="status">
            Не удалось загрузить проекты. Проверьте сеть или что backend запущен.
          </p>
        ) : null}
        {!showSkeleton && !showEmpty
          ? columns.map((column, index) => (
              <ProjectStatusColumn
                key={column.id}
                column={column}
                columnIndex={index}
                onOpenProject={onOpenProject}
                mobileHidden={index !== activeColumnIndex}
              />
            ))
          : null}
      </div>
    </section>
  );
}
