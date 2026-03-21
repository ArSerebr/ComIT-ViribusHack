import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import { useEffect, useRef } from "react";
import { assets } from "../../assets";
import { MENU_ITEMS } from "../../data/dashboardData";
import { NotificationsPopover } from "./NotificationsPopover";

const MENU_SPRING = {
  type: "spring",
  stiffness: 420,
  damping: 34,
  mass: 0.82
};

const CONTROL_HOVER = { y: -2, scale: 1.03 };
const CONTROL_TAP = { y: 0, scale: 0.97 };

export function TopBar({
  activeTab,
  aiAssistantEnabled,
  isAiOpen,
  isNotificationsOpen,
  notificationItems,
  onCloseNotifications,
  onGoHome,
  onMenuClick,
  onOpenNotification,
  onToggleNotifications,
  isNewsView = false
}) {
  const topActionsRef = useRef(null);

  useEffect(() => {
    if (!isNotificationsOpen) {
      return undefined;
    }

    const handlePointerDown = (event) => {
      if (!topActionsRef.current?.contains(event.target)) {
        onCloseNotifications();
      }
    };

    const handleEscape = (event) => {
      if (event.key === "Escape") {
        onCloseNotifications();
      }
    };

    window.addEventListener("pointerdown", handlePointerDown);
    window.addEventListener("keydown", handleEscape);

    return () => {
      window.removeEventListener("pointerdown", handlePointerDown);
      window.removeEventListener("keydown", handleEscape);
    };
  }, [isNotificationsOpen, onCloseNotifications]);

  return (
    <header className={`top-bar ${isNewsView ? "top-bar-news" : ""}`}>
      <motion.button
        className="logo-wrap"
        onClick={onGoHome}
        type="button"
        aria-label="На главную"
        whileHover={CONTROL_HOVER}
        whileTap={CONTROL_TAP}
      >
        <img src={assets.untitledLogo} alt="" className="logo-icon" />
        <span className="logo-text">ComIT</span>
      </motion.button>

      <LayoutGroup id="top-bar-menu">
        <nav className="menu-nav" aria-label="Основное меню">
          {MENU_ITEMS.map((item) => {
            const isAi = item.id === "ai";
            const isActive = !isAi && activeTab === item.id;
            const aiActive = isAi && (aiAssistantEnabled || isAiOpen);
            const iconSrc = item.icons[isAi ? (aiActive ? "active" : "inactive") : isActive ? "active" : "inactive"];

            return (
              <motion.button
                key={item.id}
                layout
                transition={MENU_SPRING}
                className={`menu-item ${isActive ? "menu-item-active" : ""} ${aiActive ? "menu-item-ai-active" : ""}`}
                onClick={() => onMenuClick(item.id)}
                type="button"
                aria-pressed={isAi ? aiActive : isActive}
                whileHover={isActive ? { y: -2, scale: 1.01 } : CONTROL_HOVER}
                whileTap={CONTROL_TAP}
              >
                {!isAi && isActive ? (
                  <motion.span className="menu-item-backdrop" layoutId="top-bar-active-pill" transition={MENU_SPRING} />
                ) : null}

                <span className="menu-item-content">
                  <motion.span
                    className={`menu-icon-wrap ${isAi ? "menu-icon-wrap-ai" : ""}`}
                    layout="position"
                    animate={isAi && aiActive ? { scale: [1, 1.08, 1], y: [0, -1, 0] } : { scale: 1, y: 0 }}
                    transition={isAi && aiActive ? { duration: 2.4, repeat: Infinity, ease: "easeInOut" } : MENU_SPRING}
                  >
                    <img src={iconSrc} alt="" className={`menu-icon ${isAi ? "menu-icon-ai" : ""}`} />
                  </motion.span>

                  <AnimatePresence initial={false}>
                    {!isAi && isActive ? (
                      <motion.span
                        key={`${item.id}-label`}
                        className="menu-label"
                        initial={{ opacity: 0, x: -10, filter: "blur(6px)" }}
                        animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
                        exit={{ opacity: 0, x: -8, filter: "blur(4px)" }}
                        transition={{ duration: 0.24, ease: [0.22, 1, 0.36, 1] }}
                      >
                        {item.label}
                      </motion.span>
                    ) : null}
                  </AnimatePresence>
                </span>
              </motion.button>
            );
          })}
        </nav>
      </LayoutGroup>

      <div className="top-actions" ref={topActionsRef}>
        <motion.button
          className={`glass-icon-button notify-btn ${isNotificationsOpen ? "glass-icon-button-active" : ""}`}
          type="button"
          aria-label="Уведомления"
          aria-expanded={isNotificationsOpen}
          onClick={onToggleNotifications}
          whileHover={CONTROL_HOVER}
          whileTap={CONTROL_TAP}
        >
          <img src={assets.bellIcon} alt="" className="notify-icon" />
          <span className="notify-dot" />
        </motion.button>

        <motion.button
          className="account-btn"
          type="button"
          aria-label="Аккаунт"
          whileHover={CONTROL_HOVER}
          whileTap={CONTROL_TAP}
        >
          <img src={assets.ellipse194} alt="" className="account-ring" />
          <img src={assets.avatarPhoto} alt="Профиль" className="account-photo" />
        </motion.button>

        <AnimatePresence>
          {isNotificationsOpen ? (
            <NotificationsPopover
              items={notificationItems}
              onClose={onCloseNotifications}
              onOpenNotification={onOpenNotification}
            />
          ) : null}
        </AnimatePresence>
      </div>
    </header>
  );
}
