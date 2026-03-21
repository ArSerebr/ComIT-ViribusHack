import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { assets } from "../../assets";

function splitTags(rawTags) {
  return rawTags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean)
    .slice(0, 8);
}

export function ArticleCreatePage({ onBack, onSubmitArticle, isSubmitting = false, drafts = [], onOpenDraft }) {
  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [tagsInput, setTagsInput] = useState("");
  const [content, setContent] = useState("");
  const [statusMessage, setStatusMessage] = useState("");

  const parsedTags = useMemo(() => splitTags(tagsInput), [tagsInput]);

  const clearForm = () => {
    setTitle("");
    setSummary("");
    setTagsInput("");
    setContent("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const normalizedTitle = title.trim();
    const normalizedSummary = summary.trim();
    const normalizedContent = content.trim();

    if (!normalizedTitle || !normalizedSummary || !normalizedContent) {
      setStatusMessage("Заполните заголовок, краткое описание и текст статьи.");
      return;
    }

    const created = await onSubmitArticle({
      title: normalizedTitle,
      summary: normalizedSummary,
      content: normalizedContent,
      tags: parsedTags
    });

    if (created) {
      setStatusMessage("Черновик статьи сохранен.");
      clearForm();
      return;
    }

    setStatusMessage("Не удалось сохранить черновик. Попробуйте снова.");
  };

  return (
    <section className="article-create-page">
      <div className="article-create-head">
        <button className="news-back-btn" type="button" aria-label="Назад" onClick={onBack}>
          <img src={assets.arrowSmallLeftIcon} alt="" />
        </button>
        <div>
          <h1>Создание статьи</h1>
          <p>Соберите структуру материала, теги и описание для публикации в библиотеке.</p>
        </div>
      </div>

      <div className="article-create-layout">
        <motion.form
          className="glass-card article-create-form"
          onSubmit={handleSubmit}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <label>
            Заголовок статьи
            <input
              type="text"
              placeholder="Например: ML-критерии для A/B-тестов"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              maxLength={120}
            />
          </label>

          <label>
            Краткое описание
            <textarea
              placeholder="Коротко опишите, что читатель узнает из статьи"
              value={summary}
              onChange={(event) => setSummary(event.target.value)}
              maxLength={280}
              rows={4}
            />
          </label>

          <label>
            Теги
            <input
              type="text"
              placeholder="ml, ab-test, analytics"
              value={tagsInput}
              onChange={(event) => setTagsInput(event.target.value)}
            />
          </label>

          <div className="article-create-tags-preview">
            {parsedTags.length ? (
              parsedTags.map((tag) => (
                <span key={tag}>
                  #{tag}
                </span>
              ))
            ) : (
              <p>Добавьте теги через запятую, чтобы упростить поиск статьи.</p>
            )}
          </div>

          <label>
            Текст статьи
            <textarea
              placeholder="Основной контент статьи"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              rows={10}
            />
          </label>

          {statusMessage ? <p className="article-create-status">{statusMessage}</p> : null}

          <button type="submit" className="projects-hub-create-btn" disabled={isSubmitting}>
            <img src={assets.plusSmallIcon} alt="" />
            <span>{isSubmitting ? "Сохраняем..." : "Сохранить черновик"}</span>
          </button>
        </motion.form>

        <motion.aside
          className="glass-card article-create-drafts"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.05 }}
        >
          <h2>Последние черновики</h2>
          {drafts.length ? (
            <ul>
              {drafts.slice(0, 5).map((draft) => (
                <li key={draft.slug}>
                  <button type="button" onClick={() => onOpenDraft(draft.slug)}>
                    <strong>{draft.title}</strong>
                    <span>{draft.updatedLabel}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p>Пока нет черновиков. После сохранения они появятся здесь.</p>
          )}
        </motion.aside>
      </div>
    </section>
  );
}
