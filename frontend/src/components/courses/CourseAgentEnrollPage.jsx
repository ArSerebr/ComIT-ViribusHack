import { motion } from "framer-motion";
import { assets } from "../../assets";

/**
 * Страница записи на курс (сценарий агента). Поля с data-agent-target для плеера.
 */
export function CourseAgentEnrollPage({ onBack, userEmail = "" }) {
  return (
    <section className="course-agent-enroll-page">
      <div className="library-page-head article-reader-head">
        <button type="button" className="news-back-btn library-back-btn" aria-label="Назад" onClick={onBack}>
          <img src={assets.arrowSmallLeftIcon} alt="" />
        </button>
        <h1 className="library-page-title">Запись на курс</h1>
      </div>

      <motion.div
        className="glass-card course-agent-enroll-card"
        data-agent-target="enroll-form-root"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
      >
        <p className="course-agent-enroll-eyebrow">Запись на курс · нетология</p>
        <h2 className="course-agent-enroll-title">Курс «ML-инженер»</h2>
        <p className="course-agent-enroll-lead">
          12 месяцев: от данных и обучения моделей до внедрения и сопровождения. Заполните форму — мы подтвердим участие на
          платформе.
        </p>

        <form
          className="course-agent-enroll-form"
          onSubmit={(e) => {
            e.preventDefault();
          }}
        >
          <label className="auth-field">
            <span>Email</span>
            <input
              type="email"
              name="email"
              data-agent-target="enroll-email"
              defaultValue={userEmail}
              placeholder="you@university.ru"
              autoComplete="email"
            />
          </label>

          <label className="auth-field">
            <span>Телефон</span>
            <input type="tel" name="phone" data-agent-target="enroll-phone" placeholder="+7 …" autoComplete="tel" />
          </label>

          <label className="auth-field">
            <span>Комментарий</span>
            <textarea
              name="comment"
              data-agent-target="enroll-comment"
              rows={3}
              placeholder="Цели, удобное время связи…"
            />
          </label>

          <label className="course-agent-enroll-consent">
            <input type="checkbox" name="consent" data-agent-target="enroll-consent" />
            <span>Согласен с обработкой данных и правилами платформы</span>
          </label>

          <button type="submit" className="course-agent-enroll-submit" data-agent-target="enroll-submit">
            Отправить заявку
          </button>
        </form>
      </motion.div>
    </section>
  );
}
