import { LayoutGroup, motion } from "framer-motion";
import { MENU_ITEMS } from "../../data/dashboardData";

const MOBILE_MENU_ITEMS = MENU_ITEMS;

const ACTIVE_TAB_SPRING = {
  type: "spring",
  stiffness: 460,
  damping: 34,
  mass: 0.82
};

/**
 * Mobile chrome for feed-style pages:
 * - top pseudo-browser URL bar
 * - bottom tab dock with active animated pill
 */
export function MobileShell({ activeTab, aiAssistantEnabled, isAiOpen, onMenuClick }) {
  return (
    <div className="mobile-shell" aria-hidden={false}>
      <LayoutGroup id="mobile-tab-dock">
        <motion.nav
          className="mobile-tab-dock"
          initial={{ opacity: 0, y: 16, filter: "blur(8px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ duration: 0.36, ease: [0.22, 1, 0.36, 1], delay: 0.08 }}
          aria-label="Mobile navigation"
        >
          {MOBILE_MENU_ITEMS.map((item) => {
            const isAiItem = item.id === "ai";
            const isActive = isAiItem ? aiAssistantEnabled || isAiOpen : activeTab === item.id;
            const iconSrc = item.icons[isActive ? "active" : "inactive"];

            return (
              <motion.button
                key={item.id}
                layout
                transition={ACTIVE_TAB_SPRING}
                className={`mobile-tab-item ${isActive ? "mobile-tab-item-active" : ""} ${isAiItem ? "mobile-tab-item-ai" : ""}`}
                onClick={() => onMenuClick(item.id)}
                type="button"
                aria-pressed={isActive}
                whileTap={{ scale: 0.94 }}
              >
                {isActive ? (
                  <motion.span
                    className="mobile-tab-item-backdrop"
                    layoutId={isAiItem ? "mobile-tab-ai-pill" : "mobile-tab-active-pill"}
                    transition={ACTIVE_TAB_SPRING}
                  />
                ) : null}

                <span className="mobile-tab-item-icon-wrap">
                  <img src={iconSrc} alt="" className="mobile-tab-item-icon" />
                </span>
              </motion.button>
            );
          })}
        </motion.nav>
      </LayoutGroup>
    </div>
  );
}