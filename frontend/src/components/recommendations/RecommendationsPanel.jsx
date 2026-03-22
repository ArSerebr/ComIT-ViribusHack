import { useEffect, useRef } from "react";
import {
  AnimatePresence,
  animate,
  motion,
  useMotionTemplate,
  useMotionValue,
  useTransform
} from "framer-motion";
import { assets } from "../../assets";

const RETURN_SPRING = {
  type: "spring",
  stiffness: 340,
  damping: 28,
  mass: 0.9
};

const EXIT_SPRING = {
  type: "spring",
  stiffness: 250,
  damping: 24,
  mass: 0.88
};

const DISMISS_DISTANCE = 150;
const DISMISS_VELOCITY = 820;
const EXIT_COMPLETE_DELAY = 320;

function stopCardDrag(event) {
  event.stopPropagation();
}

const STACK_STYLE = {
  1: { "--stack-scale": 0.94, "--stack-shift-y": "6px" },
  2: { "--stack-scale": 0.9, "--stack-shift-y": "12px" }
};

function DraggableCard({
  card,
  canDismiss,
  dismissDirection,
  topCardExitAnimation,
  onDismissTopCard,
  onTopCardExitComplete,
  isLiked,
  onToggleLike,
  onOpen,
  onShare
}) {
  const dragX = useMotionValue(0);
  const dragY = useMotionValue(0);
  const cardOpacity = useMotionValue(1);
  const cardScale = useMotionValue(1);
  const hasExitedRef = useRef(false);

  const dragProgress = useTransform([dragX, dragY], ([latestX, latestY]) =>
    Math.min(1, Math.hypot(latestX, latestY) / 260)
  );
  const cardRotate = useTransform([dragX, dragY], ([latestX, latestY]) =>
    Math.max(-24, Math.min(24, latestX / 18 + latestY / 36))
  );

  const imageScale = useTransform(dragProgress, [0, 1], [1, 1.06]);
  const imageX = useTransform(dragX, [-240, 0, 240], [-14, 0, 14]);
  const imageY = useTransform(dragY, [-240, 0, 240], [-12, 0, 12]);
  const actionsY = useTransform(dragProgress, [0, 1], [0, -10]);
  const actionsScale = useTransform(dragProgress, [0, 1], [1, 1.035]);

  const glowOpacity = useTransform(dragProgress, [0, 0.18, 1], [0, 0.14, 1]);
  const glowX = useTransform(dragX, [-260, 0, 260], ["18%", "50%", "82%"]);
  const glowY = useTransform(dragY, [-260, 0, 260], ["18%", "50%", "82%"]);
  const glowBackground = useMotionTemplate`radial-gradient(circle at ${glowX} ${glowY}, rgba(255, 255, 255, 0.24) 0%, rgba(162, 106, 255, 0.22) 18%, rgba(255, 92, 176, 0.14) 34%, rgba(8, 8, 12, 0) 62%)`;

  useEffect(() => {
    if (!dismissDirection) {
      if (hasExitedRef.current) return undefined;
      dragX.set(0);
      dragY.set(0);
      cardOpacity.set(0);
      cardScale.set(0.96);
      const c1 = animate(cardOpacity, 1, { duration: 0.24, ease: [0.22, 1, 0.36, 1] });
      const c2 = animate(cardScale, 1, RETURN_SPRING);
      return () => {
        c1.stop();
        c2.stop();
      };
    }
    return undefined;
  }, [cardOpacity, cardScale, dismissDirection, dragX, dragY]);

  useEffect(() => {
    if (!dismissDirection) return undefined;

    hasExitedRef.current = true;
    const c1 = animate(dragX, topCardExitAnimation.x, EXIT_SPRING);
    const c2 = animate(dragY, topCardExitAnimation.y, EXIT_SPRING);
    const c3 = animate(cardScale, topCardExitAnimation.scale ?? 0.96, {
      duration: 0.26,
      ease: [0.22, 1, 0.36, 1]
    });
    const c4 = animate(cardOpacity, topCardExitAnimation.opacity ?? 0, {
      duration: 0.24,
      ease: [0.4, 0, 1, 1]
    });

    const timeoutId = window.setTimeout(onTopCardExitComplete, EXIT_COMPLETE_DELAY);

    return () => {
      window.clearTimeout(timeoutId);
      c1.stop();
      c2.stop();
      c3.stop();
      c4.stop();
    };
  }, [
    cardOpacity,
    cardScale,
    dismissDirection,
    dragX,
    dragY,
    onTopCardExitComplete,
    topCardExitAnimation
  ]);

  const resetDraggedCard = () => {
    animate(dragX, 0, RETURN_SPRING);
    animate(dragY, 0, RETURN_SPRING);
    animate(cardOpacity, 1, { duration: 0.18, ease: [0.22, 1, 0.36, 1] });
    animate(cardScale, 1, RETURN_SPRING);
  };

  return (
    <motion.article
      key={card.instanceId}
      className="recommendation-card top-card"
      style={{
        x: dragX,
        y: dragY,
        rotate: cardRotate,
        opacity: cardOpacity,
        scale: cardScale
      }}
      drag={canDismiss}
      dragElastic={0.12}
      dragMomentum={false}
      onDragStart={() => {
        if (!canDismiss) return;
        animate(cardScale, 1.02, { duration: 0.14, ease: [0.22, 1, 0.36, 1] });
      }}
      onDragEnd={(_, info) => {
        if (!canDismiss) return;
        const projectedX = info.offset.x + info.velocity.x * 0.18;
        const projectedY = info.offset.y + info.velocity.y * 0.18;
        const velocity = Math.hypot(info.velocity.x, info.velocity.y);
        if (
          Math.hypot(projectedX, projectedY) > DISMISS_DISTANCE ||
          velocity > DISMISS_VELOCITY
        ) {
          onDismissTopCard({ x: projectedX, y: projectedY });
          return;
        }
        resetDraggedCard();
      }}
    >
      <motion.div
        className="recommendation-drag-glow"
        style={{ opacity: glowOpacity, background: glowBackground }}
      />
      <motion.div
        style={{
          width: "100%",
          height: "100%",
          scale: imageScale,
          x: imageX,
          y: imageY
        }}
      >
        <img
          className="recommendation-image recommendation-image-hero"
          src={card.image}
          alt={card.title}
          draggable={false}
        />
      </motion.div>
      <motion.div
        className="recommendation-actions"
        style={{ y: actionsY, scale: actionsScale }}
      >
        <motion.button
          className={`action-btn ${isLiked ? "action-btn-active" : ""}`}
          type="button"
          aria-label="Лайкнуть"
          onPointerDown={stopCardDrag}
          onClick={() => onToggleLike(card.id)}
          whileHover={{ y: -3, scale: 1.04 }}
          whileTap={{ scale: 0.92 }}
        >
          <AnimatePresence initial={false}>
            {isLiked ? (
              <motion.span
                key="like-burst"
                className="action-btn-burst"
                initial={{ opacity: 0, scale: 0.55 }}
                animate={{ opacity: [0, 0.85, 0], scale: [0.55, 1.18, 1.38] }}
                exit={{ opacity: 0, scale: 1.42 }}
                transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
              />
            ) : null}
          </AnimatePresence>
          <motion.img
            src={isLiked ? assets.heartFilledIcon : assets.heartOutlineIcon}
            alt=""
            className={isLiked ? "action-btn-icon-active" : ""}
            animate={isLiked ? { scale: [1, 1.18, 1], rotate: [0, -10, 0] } : { scale: 0.94, rotate: 0 }}
            transition={{ duration: 0.34, ease: [0.22, 1, 0.36, 1] }}
          />
        </motion.button>
        <motion.button
          className="action-btn action-btn-open"
          type="button"
          aria-label="Открыть ссылку"
          onPointerDown={stopCardDrag}
          onClick={() => onOpen(card)}
          whileHover={{ y: -3, scale: 1.04 }}
          whileTap={{ scale: 0.94 }}
        >
          <img src={assets.linkAltIcon} alt="" />
        </motion.button>
        <motion.button
          className="action-btn action-btn-share"
          type="button"
          aria-label="Поделиться"
          onPointerDown={stopCardDrag}
          onClick={() => onShare(card)}
          whileHover={{ y: -3, scale: 1.04 }}
          whileTap={{ scale: 0.94 }}
        >
          <img src={assets.shareIcon} alt="" />
        </motion.button>
      </motion.div>
    </motion.article>
  );
}

function MobileRecoOverlay({
  topCard,
  stackedCards,
  canDismiss,
  dismissDirection,
  topCardExitAnimation,
  onDismissTopCard,
  onTopCardExitComplete,
  likedRecommendations,
  onToggleRecommendationLike,
  onShareRecommendation,
  onOpenRecommendation,
  onClose,
  totalCount
}) {
  const dragY = useMotionValue(0);
  const cardOpacity = useMotionValue(1);
  const cardScale = useMotionValue(1);

  const cardRotate = useTransform(dragY, [-200, 0, 200], [-4, 0, 4]);

  useEffect(() => {
    if (!topCard || dismissDirection) return undefined;
    dragY.set(0);
    cardOpacity.set(0);
    cardScale.set(0.96);
    const controls = [
      animate(cardOpacity, 1, { duration: 0.24, ease: [0.22, 1, 0.36, 1] }),
      animate(cardScale, 1, RETURN_SPRING)
    ];
    return () => controls.forEach((c) => c.stop());
  }, [cardOpacity, cardScale, dismissDirection, dragY, topCard]);

  useEffect(() => {
    if (!topCard || !dismissDirection) return undefined;
    const controls = [
      animate(dragY, topCardExitAnimation.y, EXIT_SPRING),
      animate(cardScale, topCardExitAnimation.scale ?? 0.96, { duration: 0.26, ease: [0.22, 1, 0.36, 1] }),
      animate(cardOpacity, topCardExitAnimation.opacity ?? 0, { duration: 0.24, ease: [0.4, 0, 1, 1] })
    ];
    const timeoutId = window.setTimeout(() => {
      onTopCardExitComplete();
    }, EXIT_COMPLETE_DELAY);
    return () => {
      window.clearTimeout(timeoutId);
      controls.forEach((c) => c.stop());
    };
  }, [cardOpacity, cardScale, dismissDirection, dragY, onTopCardExitComplete, topCard, topCardExitAnimation]);

  const resetDrag = () => {
    animate(dragY, 0, RETURN_SPRING);
    animate(cardOpacity, 1, { duration: 0.18, ease: [0.22, 1, 0.36, 1] });
    animate(cardScale, 1, RETURN_SPRING);
  };

  const isTopCardLiked = topCard ? Boolean(likedRecommendations[topCard.id]) : false;
  const currentIndex = totalCount - (stackedCards.length + (topCard ? 1 : 0));

  return (
    <motion.div
      className="mobile-reco-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.22 }}
    >
      <button className="mobile-reco-close" type="button" aria-label="Закрыть" onClick={onClose}>
        <img src={assets.group12021Icon} alt="" />
      </button>

      <AnimatePresence mode="wait">
        {topCard ? (
          <motion.div
            key={topCard.instanceId}
            className="mobile-reco-card-wrap"
            drag={canDismiss ? "y" : false}
            dragElastic={0.08}
            dragMomentum={false}
            style={{ y: dragY, rotate: cardRotate, opacity: cardOpacity, scale: cardScale }}
            onDragStart={() => {
              if (!canDismiss) return;
              animate(cardScale, 1.02, { duration: 0.14, ease: [0.22, 1, 0.36, 1] });
            }}
            onDragEnd={(_, info) => {
              if (!canDismiss) return;
              const projectedY = info.offset.y + info.velocity.y * 0.18;
              const velocityY = Math.abs(info.velocity.y);
              if (Math.abs(projectedY) > DISMISS_DISTANCE || velocityY > DISMISS_VELOCITY) {
                onDismissTopCard({ x: 0, y: projectedY });
                return;
              }
              resetDrag();
            }}
          >
            <span className="mobile-reco-counter">
              {currentIndex + 1} / {totalCount}
            </span>
            <img className="mobile-reco-image" src={topCard.image} alt={topCard.title} draggable={false} />
          </motion.div>
        ) : (
          <div
            className="mobile-reco-card-wrap"
            style={{ display: "flex", alignItems: "center", justifyContent: "center" }}
          >
            <p style={{ color: "rgba(255,255,255,0.5)", fontSize: 18 }}>Карточки закончились</p>
          </div>
        )}
      </AnimatePresence>

      <div className="mobile-reco-actions">
        {topCard ? (
          <>
            <motion.button
              className={`action-btn ${isTopCardLiked ? "action-btn-active" : ""}`}
              type="button"
              aria-label="Лайкнуть"
              onPointerDown={stopCardDrag}
              onClick={() => onToggleRecommendationLike(topCard.id)}
              whileHover={{ y: -3, scale: 1.04 }}
              whileTap={{ scale: 0.92 }}
            >
              <AnimatePresence initial={false}>
                {isTopCardLiked ? (
                  <motion.span
                    key="like-burst"
                    className="action-btn-burst"
                    initial={{ opacity: 0, scale: 0.55 }}
                    animate={{ opacity: [0, 0.85, 0], scale: [0.55, 1.18, 1.38] }}
                    exit={{ opacity: 0, scale: 1.42 }}
                    transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
                  />
                ) : null}
              </AnimatePresence>
              <motion.img
                src={isTopCardLiked ? assets.heartFilledIcon : assets.heartOutlineIcon}
                alt=""
                className={isTopCardLiked ? "action-btn-icon-active" : ""}
                animate={isTopCardLiked ? { scale: [1, 1.18, 1], rotate: [0, -10, 0] } : { scale: 0.94, rotate: 0 }}
                transition={{ duration: 0.34, ease: [0.22, 1, 0.36, 1] }}
              />
            </motion.button>
            <motion.button
              className="action-btn action-btn-open"
              type="button"
              aria-label="Открыть ссылку"
              onPointerDown={stopCardDrag}
              onClick={() => onOpenRecommendation(topCard)}
              whileHover={{ y: -3, scale: 1.04 }}
              whileTap={{ scale: 0.94 }}
            >
              <img src={assets.linkAltIcon} alt="" />
            </motion.button>
            <motion.button
              className="action-btn action-btn-share"
              type="button"
              aria-label="Поделиться"
              onPointerDown={stopCardDrag}
              onClick={() => onShareRecommendation(topCard)}
              whileHover={{ y: -3, scale: 1.04 }}
              whileTap={{ scale: 0.94 }}
            >
              <img src={assets.shareIcon} alt="" />
            </motion.button>
          </>
        ) : null}
      </div>
    </motion.div>
  );
}

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
  onOpenRecommendation,
  onShareRecommendation,
  isLoading = false
}) {
  const totalCount = stackedCards.length + (topCard ? 1 : 0);

  return (
    <>
      <button
        className="deck-fab"
        type="button"
        aria-label={isOpen ? "Скрыть карточки" : "Показать карточки"}
        aria-expanded={isOpen}
        onClick={onToggleOpen}
      >
        <img src={assets.recommendationCardsIcon} alt="" />
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

            <div className={`deck-wrap${isLoading ? " deck-wrap--busy" : ""}`} aria-busy={isLoading || undefined}>
              {stackedCards
                .slice()
                .reverse()
                .map((card, index) => (
                  <motion.article
                    key={card.instanceId}
                    className={`recommendation-card stacked-card stacked-${index + 1}`}
                    style={STACK_STYLE[index + 1] || STACK_STYLE[2]}
                  >
                    <img className="recommendation-image" src={card.image} alt={card.title} draggable={false} />
                  </motion.article>
                ))}

              <AnimatePresence mode="wait">
                {topCard ? (
                  <DraggableCard
                    key={topCard.instanceId}
                    card={topCard}
                    canDismiss={canDismiss}
                    dismissDirection={dismissDirection}
                    topCardExitAnimation={topCardExitAnimation}
                    onDismissTopCard={onDismissTopCard}
                    onTopCardExitComplete={onTopCardExitComplete}
                    isLiked={Boolean(likedRecommendations[topCard.id])}
                    onToggleLike={onToggleRecommendationLike}
                    onOpen={onOpenRecommendation}
                    onShare={onShareRecommendation}
                  />
                ) : null}
              </AnimatePresence>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isOpen && (
          <MobileRecoOverlay
            topCard={topCard}
            stackedCards={stackedCards}
            canDismiss={canDismiss}
            dismissDirection={dismissDirection}
            topCardExitAnimation={topCardExitAnimation}
            onDismissTopCard={onDismissTopCard}
            onTopCardExitComplete={onTopCardExitComplete}
            likedRecommendations={likedRecommendations}
            onToggleRecommendationLike={onToggleRecommendationLike}
            onShareRecommendation={onShareRecommendation}
            onOpenRecommendation={onOpenRecommendation}
            onClose={onClose}
            totalCount={totalCount}
          />
        )}
      </AnimatePresence>
    </>
  );
}
