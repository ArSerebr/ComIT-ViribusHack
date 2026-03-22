import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { assets } from "../../assets";

const VISIBILITY_OPTIONS = [
  { value: "private", label: "Приватный" },
  { value: "public",  label: "Публичный" },
];

function CustomSelect({ value, onChange, options }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (!open) return;
    const handleClick = (e) => { if (!ref.current?.contains(e.target)) setOpen(false); };
    document.addEventListener("pointerdown", handleClick);
    return () => document.removeEventListener("pointerdown", handleClick);
  }, [open]);

  const selected = options.find((o) => o.value === value);

  return (
    <div className="custom-select" ref={ref}>
      <button
        type="button"
        className={`custom-select-trigger ${open ? "custom-select-trigger-open" : ""}`}
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span>{selected?.label}</span>
        <svg className="custom-select-chevron" width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M3 5l4 4 4-4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
      <AnimatePresence>
        {open && (
          <motion.ul
            className="custom-select-menu"
            role="listbox"
            initial={{ opacity: 0, y: -6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.97 }}
            transition={{ duration: 0.15, ease: [0.22, 1, 0.36, 1] }}
          >
            {options.map((opt) => (
              <li
                key={opt.value}
                role="option"
                aria-selected={opt.value === value}
                className={`custom-select-option ${opt.value === value ? "custom-select-option-active" : ""}`}
                onPointerDown={() => { onChange(opt.value); setOpen(false); }}
              >
                {opt.label}
                {opt.value === value && (
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M2.5 7l3.5 3.5 5.5-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}

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
            <CustomSelect
              value={visibility}
              onChange={setVisibility}
              options={VISIBILITY_OPTIONS}
            />
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
