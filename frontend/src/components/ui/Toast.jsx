import { AnimatePresence, motion } from "framer-motion";

const VARIANTS = {
  initial: { opacity: 0, y: 24, scale: 0.95, filter: "blur(6px)" },
  animate: { opacity: 1, y: 0, scale: 1, filter: "blur(0px)" },
  exit:    { opacity: 0, y: 16, scale: 0.96, filter: "blur(4px)" },
};

const TRANSITION = { type: "spring", stiffness: 380, damping: 28 };

/** Глобальный стек тостов. Рендерится в App, управляется через useToast. */
export function ToastStack({ toasts, onDismiss }) {
  return (
    <div className="toast-stack" aria-live="polite">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <motion.div
            key={toast.id}
            className={`toast toast-${toast.type ?? "info"}`}
            variants={VARIANTS}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={TRANSITION}
            layout
          >
            <span className="toast-icon" aria-hidden="true" />
            <p className="toast-message">{toast.message}</p>
            <button
              type="button"
              className="toast-close"
              aria-label="Закрыть"
              onClick={() => onDismiss(toast.id)}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
