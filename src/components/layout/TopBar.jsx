import { assets } from "../../assets";
import { MENU_ITEMS } from "../../data/dashboardData";

export function TopBar({ activeTab, aiAssistantEnabled, onGoHome, onMenuClick, isNewsView = false }) {
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
          const isAiExpanded = isAi && activeTab === "chat";
          const aiActive = isAi && aiAssistantEnabled;
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

      <div className="top-actions">
        <button className="glass-icon-button notify-btn" type="button" aria-label="Уведомления">
          <img src={assets.bellIcon} alt="" className="notify-icon" />
          <span className="notify-dot" />
        </button>
        <button className="account-btn" type="button" aria-label="Аккаунт">
          <img src={assets.ellipse194} alt="" className="account-ring" />
          <img src={assets.avatarPhoto} alt="Профиль" className="account-photo" />
        </button>
      </div>
    </header>
  );
}
