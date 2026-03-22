import { useState } from "react";
import { motion } from "framer-motion";
import { assets } from "../../assets";

export function AuthPage({
  mode = "register",
  isSubmitting = false,
  errorMessage = "",
  successMessage = "",
  onSubmitAuth,
  onSwitchMode,
  onBack
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState("");

  const isRegister = mode === "register";

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLocalError("");
    const normalizedEmail = email.trim();

    if (!normalizedEmail || !password) {
      setLocalError("Введите email и пароль.");
      return;
    }

    if (isRegister && password !== confirmPassword) {
      setLocalError("Пароли не совпадают.");
      return;
    }

    await onSubmitAuth({ mode, email: normalizedEmail, password });
  };

  return (
    <section className="auth-page">
      <button type="button" className="news-back-btn auth-back-btn" aria-label="Назад" onClick={onBack}>
        <img src={assets.arrowSmallLeftIcon} alt="" />
      </button>

      <div className="auth-page-background" aria-hidden="true" />

      <motion.div
        className="auth-page-logo"
        initial={{ opacity: 0, y: -14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.32 }}
      >
        <img src={assets.untitledLogo} alt="" />
        <strong>ComIT</strong>
      </motion.div>

      <motion.form
        className="glass-card auth-form-card"
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, delay: 0.06 }}
        onSubmit={handleSubmit}
      >
        <h1>{isRegister ? "Зарегистрируйся чтобы открыть весь потенциал ComIT" : "Войдите, чтобы продолжить работу в ComIT"}</h1>

        <p className="auth-form-subtitle">
          Согласитесь с правилами политики конфиденциальности и условиями использования платформы.
        </p>

        <label className="auth-field">
          <span>Email</span>
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Введите почту" />
        </label>

        <label className="auth-field">
          <span>Пароль</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Введите пароль"
          />
        </label>

        {isRegister ? (
          <label className="auth-field">
            <span>Повторите пароль</span>
            <input
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="Повторите пароль"
            />
          </label>
        ) : null}

        {localError ? <p className="auth-form-error">{localError}</p> : null}
        {errorMessage ? <p className="auth-form-error">{errorMessage}</p> : null}
        {successMessage ? <p className="auth-form-success">{successMessage}</p> : null}

        <button type="submit" className="auth-submit-btn" disabled={isSubmitting}>
          <span>{isSubmitting ? "Отправляем..." : isRegister ? "Создать аккаунт" : "Войти"}</span>
          <img src={assets.arrow16Icon} alt="" />
        </button>

        <p className="auth-switch-row">
          {isRegister ? "Уже есть аккаунт?" : "Нет аккаунта?"}
          <button type="button" onClick={onSwitchMode}>
            {isRegister ? "Войти" : "Создать"}
          </button>
        </p>
      </motion.form>
    </section>
  );
}
