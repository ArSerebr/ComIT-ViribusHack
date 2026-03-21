import { motion } from "framer-motion";
import { assets } from "../../assets";
import { ProjectStatusColumn } from "./ProjectStatusColumn";

export function ProjectHubPage({ columns, onBack, onCreateProject, onOpenProject }) {
  return (
    <section className="projects-hub-page">
      <div className="projects-hub-head">
        <div className="projects-hub-title-wrap">
          <button className="news-back-btn projects-hub-back-btn" type="button" aria-label="Назад на главную" onClick={onBack}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <h1 className="projects-hub-title">Проекты университета</h1>
        </div>

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

      <div className="projects-hub-columns">
        {columns.map((column, index) => (
          <ProjectStatusColumn key={column.id} column={column} columnIndex={index} onOpenProject={onOpenProject} />
        ))}
      </div>
    </section>
  );
}
