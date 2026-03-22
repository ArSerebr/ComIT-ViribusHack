import { useState } from "react";
import { motion } from "framer-motion";
import { assets } from "../../assets";

export function ProjectCreatePage({
  onBack,
  onSubmitProject,
  isSubmitting = false,
  drafts = [],
  onOpenDraft,
  isAuthenticated = false,
  onOpenAuth
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [teamName, setTeamName] = useState("");
  const [visibility, setVisibility] = useState("private");
  const [statusMessage, setStatusMessage] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const normalizedTitle = title.trim();
    const normalizedDescription = description.trim();
    const normalizedTeam = teamName.trim();

    if (!normalizedTitle || !normalizedDescription || !normalizedTeam) {
      setStatusMessage("Заполните название, описание и название команды.");
      return;
    }

    const result = await onSubmitProject({
      title: normalizedTitle,
      description: normalizedDescription,
      teamName: normalizedTeam,
      visibility
    });

    if (result && typeof result === "object" && "savedToServer" in result) {
      if (result.savedToServer) {
        setStatusMessage("Проект сохранён на сервере — он в хабе и в панели администратора.");
      } else if (result.errorMessage) {
        setStatusMessage(
          `Сервер не принял проект: ${result.errorMessage}. Копия осталась в локальных черновиках.`
        );
      } else {
        setStatusMessage(
          "Сохранено только локально. Войдите в аккаунт — тогда проект отправится в общую базу при создании."
        );
      }
      setTitle("");
      setDescription("");
      setTeamName("");
      setVisibility("private");
      return;
    }

    if (result) {
      setTitle("");
      setDescription("");
      setTeamName("");
      setVisibility("private");
      setStatusMessage("Черновик сохранён.");
      return;
    }

    setStatusMessage("Не удалось сохранить проект.");
  };

  return (
    <section className="project-create-page">
      <div className="project-create-head">
        <button className="news-back-btn projects-hub-back-btn" type="button" aria-label="Назад" onClick={onBack}>
          <img src={assets.arrowSmallLeftIcon} alt="" />
        </button>
        <div>
          <h1>Создание проекта</h1>
          <p>Оформите карточку проекта, чтобы команда могла подключиться и начать работу.</p>
          {!isAuthenticated ? (
            <p className="project-create-auth-hint">
              Чтобы проект сохранился в общей базе (и отображался в админке),{" "}
              <button type="button" className="project-create-auth-link" onClick={onOpenAuth}>
                войдите в аккаунт
              </button>
              .
            </p>
          ) : null}
        </div>
      </div>

      <div className="project-create-layout">
        <motion.form
          className="glass-card project-create-form"
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <label>
            Название проекта
            <input
              type="text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Например: Campus Event Hub"
              maxLength={120}
            />
          </label>

          <label>
            Описание проекта
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Кратко опишите цель и текущую задачу проекта"
              rows={5}
              maxLength={600}
            />
          </label>

          <label>
            Команда
            <input
              type="text"
              value={teamName}
              onChange={(event) => setTeamName(event.target.value)}
              placeholder="Название команды"
              maxLength={80}
            />
          </label>

          <label>
            Видимость
            <select value={visibility} onChange={(event) => setVisibility(event.target.value)}>
              <option value="private">Приватный</option>
              <option value="public">Публичный</option>
            </select>
          </label>

          {statusMessage ? <p className="project-create-status">{statusMessage}</p> : null}

          <button type="submit" className="projects-hub-create-btn" disabled={isSubmitting}>
            <img src={assets.plusSmallIcon} alt="" />
            <span>{isSubmitting ? "Сохраняем..." : "Создать проект"}</span>
          </button>
        </motion.form>

        <motion.aside
          className="glass-card project-create-drafts"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.05 }}
        >
          <h2>Мои проекты</h2>
          {drafts.length ? (
            <ul>
              {drafts.slice(0, 6).map((draft) => (
                <li key={draft.id}>
                  <button type="button" onClick={() => onOpenDraft(draft.id)}>
                    <strong>{draft.title}</strong>
                    <span>{draft.updatedLabel}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p>После создания проекта карточки появятся в этом блоке и в хабе проектов.</p>
          )}
        </motion.aside>
      </div>
    </section>
  );
}
