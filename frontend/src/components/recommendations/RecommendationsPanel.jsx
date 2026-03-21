import { useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { assets } from "../../assets";

export function RecommendationsPanel({
  isOpen,
  onToggleOpen,
  onClose,
  stackedCards,
  topCard,
  canDismiss,
  dismissDirection,
  topCardExitAnimation,
  onDismissTopCard,
  onTopCardExitComplete,
  likedRecommendations,
  onToggleRecommendationLike,
  onShareRecommendation
}) {
  const wheelLockRef = useRef(false);

  return (
    <>
      <button
        className="deck-fab"
        type="button"
        aria-label={isOpen ? "Скрыть карточки" : "Показать карточки"}
        aria-expanded={isOpen}
        onClick={onToggleOpen}
      >
        <img src={assets.folderOpenIcon} alt="" />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.aside
            className="recommendations-popover"
            initial={{ opacity: 0, y: 24, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.97 }}
            transition={{ duration: 0.22 }}
          >
            <button className="deck-close-btn" type="button" aria-label="Закрыть карточки" onClick={onClose}>
              <img src={assets.group12021Icon} alt="" />
            </button>

            <div className="deck-wrap">
              {stackedCards
                .slice()
                .reverse()
                .map((card, index) => (
                  <motion.article
                    key={card.instanceId}
                    className={`recommendation-card stacked-card stacked-${index + 1}`}
                    initial={{ opacity: 0, scale: 0.96 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.22 }}
                  >
                    <img className="recommendation-image" src={card.image} alt={card.title} />
                  </motion.article>
                ))}

              <AnimatePresence mode="wait">
                {topCard ? (
                  <motion.article
                    key={topCard.instanceId}
                    className="recommendation-card top-card"
                    drag={canDismiss}
                    dragElastic={0.18}
                    dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
                    onDragEnd={(_, info) => {
                      if (!canDismiss) {
                        return;
                      }

                      if (Math.abs(info.offset.x) > 110) {
                        onDismissTopCard(info.offset.x > 0 ? "right" : "left");
                        return;
                      }

                      if (Math.abs(info.offset.y) > 110) {
                        onDismissTopCard("down");
                      }
                    }}
                    onWheel={(event) => {
                      if (wheelLockRef.current || !canDismiss) {
                        return;
                      }
                      if (event.deltaY > 28) {
                        wheelLockRef.current = true;
                        onDismissTopCard("right");
                        window.setTimeout(() => {
                          wheelLockRef.current = false;
                        }, 340);
                      }
                    }}
                    initial={{ opacity: 0, y: 25, rotate: 8 }}
                    animate={dismissDirection ? topCardExitAnimation : { x: 0, y: 0, rotate: 0, opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ type: "spring", stiffness: 230, damping: 24 }}
                    onAnimationComplete={onTopCardExitComplete}
                  >
                    <img className="recommendation-image" src={topCard.image} alt={topCard.title} />
                    <div className="recommendation-actions">
                      <button
                        className="action-btn"
                        type="button"
                        aria-label="Лайкнуть"
                        onClick={() => onToggleRecommendationLike(topCard.id)}
                      >
                        <img src={likedRecommendations[topCard.id] ? assets.heartFilledIcon : assets.heartOutlineIcon} alt="" />
                      </button>
                      <button
                        className="action-btn"
                        type="button"
                        aria-label="Открыть ссылку"
                        onClick={() => window.open(topCard.link, "_blank", "noopener,noreferrer")}
                      >
                        <img src={assets.linkAltIcon} alt="" />
                      </button>
                      <button
                        className="action-btn"
                        type="button"
                        aria-label="Поделиться"
                        onClick={() => onShareRecommendation(topCard)}
                      >
                        <img src={assets.shareIcon} alt="" />
                      </button>
                    </div>
                  </motion.article>
                ) : null}
              </AnimatePresence>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
