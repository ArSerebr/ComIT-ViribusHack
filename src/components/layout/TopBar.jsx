import { AnimatePresence } from "framer-motion";
import { useEffect, useRef } from "react";
import { assets } from "../../assets";
import { MENU_ITEMS } from "../../data/dashboardData";
import { NotificationsPopover } from "./NotificationsPopover";

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
      <button className="logo-wrap" onClick={onGoHome} type="button" aria-label="На главную">
        <img src={assets.untitledLogo} alt="" className="logo-icon" />
        <span className="logo-text">ComIT</span>
      </button>

      <nav className="menu-nav" aria-label="Основное меню">
        {MENU_ITEMS.map((item) => {
          const isAi = item.id === "ai";
          const isActive = !isAi && activeTab === item.id;
          const isAiExpanded = isAi && isAiOpen;
          const aiActive = isAi && (aiAssistantEnabled || isAiOpen);
          const isExpanded = isActive || isAiExpanded;

          return (
            <button
              key={item.id}
              className={`menu-item ${isExpanded ? "menu-item-active" : ""} ${aiActive ? "menu-item-ai-active" : ""}`}
              onClick={() => onMenuClick(item.id)}
              type="button"
              aria-pressed={isExpanded || aiActive}
            >
              {isAi ? (
                <span className="menu-ai-icon">
                  <img src={item.icon[0]} alt="" />
                  <img src={item.icon[1]} alt="" />
                </span>
              ) : (
                <img src={item.icon} alt="" className="menu-icon" />
              )}
              {(!isAi || isAiExpanded) && <span className="menu-label">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="top-actions" ref={topActionsRef}>
        <button
          className={`glass-icon-button notify-btn ${isNotificationsOpen ? "glass-icon-button-active" : ""}`}
          type="button"
          aria-label="Уведомления"
          aria-expanded={isNotificationsOpen}
          onClick={onToggleNotifications}
        >
          <img src={assets.bellIcon} alt="" className="notify-icon" />
          <span className="notify-dot" />
        </button>

        <button className="account-btn" type="button" aria-label="Аккаунт">
          <img src={assets.ellipse194} alt="" className="account-ring" />
          <img src={assets.avatarPhoto} alt="Профиль" className="account-photo" />
        </button>

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
