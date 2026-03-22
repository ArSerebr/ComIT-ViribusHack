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
  const showSkeleton = isLoading && !columns?.length;
  const showEmpty = !showSkeleton && !columns?.length && isError && !useStaticFallback;

  return (
    <section className="projects-hub-page">
      <div className="projects-hub-head">
        <div className="projects-hub-title-wrap">
          <button className="news-back-btn projects-hub-back-btn" type="button" aria-label="Назад на главную" onClick={onBack}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <h1 className="projects-hub-title">Проекты университета</h1>
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

          <motion.button
            className="projects-hub-filter-btn"
            type="button"
            aria-label="Фильтры проектов"
            initial={{ opacity: 0, x: 18 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.16, duration: 0.3 }}
            whileHover={{ y: -2, scale: 1.03 }}
            whileTap={{ scale: 0.96 }}
          >
            <span className="projects-hub-filter-icon" aria-hidden="true" />
          </motion.button>
        </div>
      </div>

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
              <ProjectStatusColumn key={column.id} column={column} columnIndex={index} onOpenProject={onOpenProject} />
            ))
          : null}
      </div>
    </section>
  );
}
