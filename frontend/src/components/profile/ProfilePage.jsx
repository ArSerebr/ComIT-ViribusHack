import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { assets } from "../../assets";

function SummaryCard({ title, value, caption, delay = 0 }) {
  return (
    <motion.article
      className="glass-card profile-summary-card"
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
    >
      <span>{title}</span>
      <strong>{value}</strong>
      <p>{caption}</p>
    </motion.article>
  );
}

export function ProfilePage({
  user,
  isLoading = false,
  isAuthenticated = false,
  articleDraftCount = 0,
  projectDraftCount = 0,
  onBack,
  onOpenAuth,
  onLogout,
  onSaveProfile,
  onOpenArticleCreate,
  onOpenProjectCreate,
  onOpenLibrary
}) {
  const [email, setEmail] = useState("");
  const [nextPassword, setNextPassword] = useState("");
  const [status, setStatus] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setEmail(user?.email ?? "");
  }, [user?.email]);

  const roleLabel = useMemo(() => {
    if (!user?.role) return "Гость";
    if (user.role === "admin") return "Администратор";
    if (user.role === "moderator") return "Модератор";
    return "Участник";
  }, [user?.role]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!isAuthenticated) {
      return;
    }

    const payload = {};
    if (email.trim() && email.trim() !== user?.email) {
      payload.email = email.trim();
    }
    if (nextPassword.trim()) {
      payload.password = nextPassword.trim();
    }

    if (!Object.keys(payload).length) {
      setStatus("Нет изменений для сохранения.");
      return;
    }

    setIsSaving(true);
    const ok = await onSaveProfile(payload);
    setIsSaving(false);

    if (ok) {
      setStatus("Профиль обновлен.");
      setNextPassword("");
      return;
    }

    setStatus("Не удалось обновить профиль.");
  };

  if (!isAuthenticated) {
    return (
      <section className="profile-page profile-page-guest">
        <div className="profile-head">
          <button className="news-back-btn" type="button" aria-label="Назад" onClick={onBack}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <h1>Профиль</h1>
        </div>

        <motion.article
          className="glass-card profile-guest-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.32 }}
        >
          <h2>Войдите в аккаунт</h2>
          <p>Чтобы редактировать профиль, создавать статьи и управлять проектами, нужно авторизоваться.</p>
          <button type="button" className="projects-hub-create-btn" onClick={onOpenAuth}>
            <img src={assets.plusSmallIcon} alt="" />
            <span>Открыть авторизацию</span>
          </button>
        </motion.article>
      </section>
    );
  }

  return (
    <section className="profile-page">
      <div className="profile-head">
        <button className="news-back-btn" type="button" aria-label="Назад" onClick={onBack}>
          <img src={assets.arrowSmallLeftIcon} alt="" />
        </button>
        <h1>Профиль</h1>
      </div>

      <div className="profile-layout">
        <motion.article
          className="glass-card profile-main-card"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="profile-main-top">
            <img src={assets.avatarPhoto} alt="Фото профиля" />
            <div>
              <strong>{user?.email || "Пользователь"}</strong>
              <p>{roleLabel}</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="profile-form">
            <label>
              Email
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="example@mail.com"
                disabled={isLoading}
              />
            </label>

            <label>
              Новый пароль
              <input
                type="password"
                value={nextPassword}
                onChange={(event) => setNextPassword(event.target.value)}
                placeholder="Оставьте пустым, если менять не нужно"
                disabled={isLoading}
              />
            </label>

            {status ? <p className="profile-status">{status}</p> : null}

            <div className="profile-main-actions">
              <button type="submit" className="projects-hub-create-btn" disabled={isSaving || isLoading}>
                <img src={assets.plusSmallIcon} alt="" />
                <span>{isSaving ? "Сохраняем..." : "Сохранить изменения"}</span>
              </button>

              <button type="button" className="profile-logout-btn" onClick={onLogout}>
                Выйти из аккаунта
              </button>
            </div>
          </form>
        </motion.article>

        <div className="profile-side">
          <SummaryCard title="Черновики статей" value={articleDraftCount} caption="Локально сохранено материалов" delay={0.06} />
          <SummaryCard title="Черновики проектов" value={projectDraftCount} caption="Ожидают публикации в хабе" delay={0.12} />

          <motion.article
            className="glass-card profile-shortcuts-card"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.18 }}
          >
            <h2>Быстрые действия</h2>
            <button type="button" onClick={onOpenArticleCreate}>
              Создать статью
            </button>
            <button type="button" onClick={onOpenProjectCreate}>
              Создать проект
            </button>
            <button type="button" onClick={onOpenLibrary}>
              Открыть библиотеку
            </button>
          </motion.article>
        </div>
      </div>
    </section>
  );
}
