import { useEffect, useLayoutEffect, useMemo, useRef } from "react";
import { AnimatePresence, animate, motion, useMotionValue, useTransform } from "framer-motion";
import { assets } from "../../assets";

const DISMISS_PX = 120;
const DISMISS_VEL = 500;

const EXIT_SPRING = { type: "spring", stiffness: 380, damping: 32, mass: 0.85 };

function recoKindFromCard(card) {
  const id = String(card?.id || "");
  if (id.startsWith("proj_")) return { label: "Проект", className: "reco-badge--project" };
  if (id.startsWith("course_")) return { label: "Курс", className: "reco-badge--course" };
  if (id.startsWith("article_")) return { label: "Статья", className: "reco-badge--article" };
  if (id.startsWith("hack_")) return { label: "Хакатон", className: "reco-badge--hackathon" };
  return { label: "Для вас", className: "reco-badge--default" };
}

function stopCardDrag(event) {
  event.stopPropagation();
}

/**
 * Сброс motion values при смене карточки + выход по dismissDirection через Promise (без setTimeout).
 */
function useRecoSwipeExit({ cardInstanceId, dismissDirection, exitTarget, onExitComplete }) {
  const dragX = useMotionValue(0);
  const dragY = useMotionValue(0);
  const opacity = useMotionValue(1);
  const scale = useMotionValue(1);
  const rotate = useTransform([dragX, dragY], ([x, y]) =>
    Math.max(-14, Math.min(14, (x || 0) / 22 + (y || 0) / 40))
  );

  const onDoneRef = useRef(onExitComplete);
  onDoneRef.current = onExitComplete;

  useLayoutEffect(() => {
    dragX.set(0);
    dragY.set(0);
    opacity.set(1);
    scale.set(1);
  }, [cardInstanceId, dragX, dragY, opacity, scale]);

  const exitGeneration = useRef(0);

  useEffect(() => {
    if (!dismissDirection) return undefined;

    const gen = ++exitGeneration.current;
    const targetX = exitTarget.x ?? 0;
    const targetY = exitTarget.y ?? 0;
    const targetOpacity = exitTarget.opacity ?? 0;
    const targetScale = exitTarget.scale ?? 0.94;

    let cancelled = false;

    const run = async () => {
      try {
        await Promise.all([
          animate(dragX, targetX, EXIT_SPRING),
          animate(dragY, targetY, EXIT_SPRING),
          animate(opacity, targetOpacity, { duration: 0.22, ease: [0.4, 0, 0.2, 1] }),
          animate(scale, targetScale, { duration: 0.22, ease: [0.4, 0, 0.2, 1] })
        ]);
      } catch {
        // ignore
      }
      if (!cancelled && gen === exitGeneration.current) {
        onDoneRef.current();
      }
    };

    void run();

    return () => {
      cancelled = true;
      exitGeneration.current += 1;
    };
  }, [
    dismissDirection,
    cardInstanceId,
    dragX,
    dragY,
    opacity,
    scale,
    exitTarget.x,
    exitTarget.y,
    exitTarget.opacity,
    exitTarget.scale
  ]);

  return { dragX, dragY, opacity, scale, rotate };
}

function RecoCardFace({ card, compact }) {
  const kind = recoKindFromCard(card);
  return (
    <>
      <div className="reco-deck-card__media">
        <img src={card.image} alt="" className="reco-deck-card__img" draggable={false} />
        <div className="reco-deck-card__media-shade" aria-hidden />
      </div>
      <div className={`reco-deck-card__body${compact ? " reco-deck-card__body--compact" : ""}`}>
        <span className={`reco-deck-card__badge ${kind.className}`}>{kind.label}</span>
        <h3 className="reco-deck-card__title">{card.title}</h3>
        {card.subtitle ? <p className="reco-deck-card__subtitle">{card.subtitle}</p> : null}
        {!compact ? (
          <p className="reco-deck-card__hint">Свайпните в сторону или вверх / вниз — показать следующую</p>
        ) : null}
      </div>
    </>
  );
}

function DesktopTopCard({
  card,
  canDismiss,
  dismissDirection,
  exitTarget,
  onDismissSwipe,
  onExitComplete,
  likedRecommendations,
  onToggleLike,
  onOpen,
  onShare
}) {
  const { dragX, dragY, opacity, scale, rotate } = useRecoSwipeExit({
    cardInstanceId: card.instanceId,
    dismissDirection,
    exitTarget,
    onExitComplete
  });

  const isLiked = Boolean(likedRecommendations[card.id]);

  return (
    <motion.article
      className="reco-deck-card reco-deck-card--top"
      style={{
        x: dragX,
        y: dragY,
        opacity,
        scale,
        rotate
      }}
      drag={canDismiss}
      dragConstraints={false}
      dragElastic={0.18}
      dragMomentum={false}
      whileDrag={{ cursor: "grabbing" }}
      onDragEnd={(_, info) => {
        if (!canDismiss) return;
        const ox = info.offset.x;
        const oy = info.offset.y;
        const vx = info.velocity.x;
        const vy = info.velocity.y;
        const dist = Math.hypot(ox, oy);
        const speed = Math.hypot(vx, vy);
        if (dist > DISMISS_PX || speed > DISMISS_VEL) {
          onDismissSwipe({ x: ox + vx * 0.2, y: oy + vy * 0.2 });
        } else {
          animate(dragX, 0, EXIT_SPRING);
          animate(dragY, 0, EXIT_SPRING);
        }
      }}
    >
      <RecoCardFace card={card} compact={false} />
      <div className="reco-deck-card__actions">
        <motion.button
          type="button"
          className={`reco-deck-action${isLiked ? " reco-deck-action--active" : ""}`}
          aria-label="Лайкнуть"
          onPointerDown={stopCardDrag}
          onClick={() => onToggleLike(card.id)}
          whileTap={{ scale: 0.94 }}
        >
          <img src={isLiked ? assets.heartFilledIcon : assets.heartOutlineIcon} alt="" />
        </motion.button>
        <motion.button
          type="button"
          className="reco-deck-action reco-deck-action--primary"
          aria-label="Открыть"
          onPointerDown={stopCardDrag}
          onClick={() => onOpen(card)}
          whileTap={{ scale: 0.94 }}
        >
          <img src={assets.linkAltIcon} alt="" />
        </motion.button>
        <motion.button
          type="button"
          className="reco-deck-action"
          aria-label="Поделиться"
          onPointerDown={stopCardDrag}
          onClick={() => onShare(card)}
          whileTap={{ scale: 0.94 }}
        >
          <img src={assets.shareIcon} alt="" />
        </motion.button>
      </div>
    </motion.article>
  );
}

function MobileTopCard({
  card,
  canDismiss,
  dismissDirection,
  exitTarget,
  onDismissSwipe,
  onExitComplete,
  likedRecommendations,
  onToggleLike,
  onOpen,
  onShare,
  stackIndex,
  stackTotal
}) {
  const { dragX, dragY, opacity, scale, rotate } = useRecoSwipeExit({
    cardInstanceId: card.instanceId,
    dismissDirection,
    exitTarget,
    onExitComplete
  });

  const isLiked = Boolean(likedRecommendations[card.id]);

  return (
    <motion.div
      className="reco-deck-card reco-mobile-card reco-deck-card--top"
      style={{
        x: dragX,
        y: dragY,
        opacity,
        scale,
        rotate
      }}
      drag={canDismiss}
      dragElastic={0.14}
      dragMomentum={false}
      onDragEnd={(_, info) => {
        if (!canDismiss) return;
        const ox = info.offset.x;
        const oy = info.offset.y;
        const vx = info.velocity.x;
        const vy = info.velocity.y;
        const dist = Math.hypot(ox, oy);
        const speed = Math.hypot(vx, vy);
        if (dist > DISMISS_PX || speed > DISMISS_VEL) {
          onDismissSwipe({ x: ox + vx * 0.2, y: oy + vy * 0.2 });
        } else {
          animate(dragX, 0, EXIT_SPRING);
          animate(dragY, 0, EXIT_SPRING);
        }
      }}
    >
      <span className="reco-mobile-card__counter">
        {stackIndex + 1} / {stackTotal}
      </span>
      <RecoCardFace card={card} compact />
      <div className="reco-mobile-card__actions">
        <button
          type="button"
          className={`reco-deck-action${isLiked ? " reco-deck-action--active" : ""}`}
          aria-label="Лайкнуть"
          onPointerDown={stopCardDrag}
          onClick={() => onToggleLike(card.id)}
        >
          <img src={isLiked ? assets.heartFilledIcon : assets.heartOutlineIcon} alt="" />
        </button>
        <button
          type="button"
          className="reco-deck-action reco-deck-action--primary"
          aria-label="Открыть"
          onPointerDown={stopCardDrag}
          onClick={() => onOpen(card)}
        >
          <img src={assets.linkAltIcon} alt="" />
        </button>
        <button
          type="button"
          className="reco-deck-action"
          aria-label="Поделиться"
          onPointerDown={stopCardDrag}
          onClick={() => onShare(card)}
        >
          <img src={assets.shareIcon} alt="" />
        </button>
      </div>
    </motion.div>
  );
}

function StackedPreview({ card, depth }) {
  const kind = recoKindFromCard(card);
  return (
    <div className={`reco-deck-card reco-deck-card--stack reco-deck-card--stack-${depth}`}>
      <div className="reco-deck-card__media reco-deck-card__media--stack">
        <img src={card.image} alt="" className="reco-deck-card__img" draggable={false} />
        <div className="reco-deck-card__media-shade" aria-hidden />
      </div>
      <div className="reco-deck-card__stack-caption">
        <span className={`reco-deck-card__badge ${kind.className}`}>{kind.label}</span>
        <p className="reco-deck-card__stack-title">{card.title}</p>
      </div>
    </div>
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
  const exitTarget = useMemo(
    () => ({
      x: topCardExitAnimation.x ?? 0,
      y: topCardExitAnimation.y ?? 0,
      opacity: topCardExitAnimation.opacity ?? 0,
      scale: topCardExitAnimation.scale ?? 0.94
    }),
    [
      topCardExitAnimation.x,
      topCardExitAnimation.y,
      topCardExitAnimation.opacity,
      topCardExitAnimation.scale
    ]
  );

  const totalCount = stackedCards.length + (topCard ? 1 : 0);

  return (
    <>
      <button
        className="deck-fab"
        type="button"
        aria-label={isOpen ? "Скрыть рекомендации" : "Показать рекомендации"}
        aria-expanded={isOpen}
        onClick={onToggleOpen}
      >
        <img src={assets.recommendationCardsIcon} alt="" />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.aside
            className="recommendations-popover recommendations-popover--v2"
            initial={{ opacity: 0, y: 20, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.98 }}
            transition={{ duration: 0.2 }}
          >
            <div className="reco-popover-head">
              <p className="reco-popover-head__title">Рекомендации</p>
              <button className="reco-popover-head__close" type="button" aria-label="Закрыть" onClick={onClose}>
                <img src={assets.group12021Icon} alt="" />
              </button>
            </div>

            <div className={`reco-deck-wrap${isLoading ? " reco-deck-wrap--busy" : ""}`} aria-busy={isLoading || undefined}>
              {stackedCards
                .slice()
                .reverse()
                .map((card, i) => (
                  <StackedPreview key={card.instanceId} card={card} depth={stackedCards.length - i} />
                ))}

              {topCard ? (
                <DesktopTopCard
                  key={topCard.instanceId}
                  card={topCard}
                  canDismiss={canDismiss}
                  dismissDirection={dismissDirection}
                  exitTarget={exitTarget}
                  onDismissSwipe={onDismissTopCard}
                  onExitComplete={onTopCardExitComplete}
                  likedRecommendations={likedRecommendations}
                  onToggleLike={onToggleRecommendationLike}
                  onOpen={onOpenRecommendation}
                  onShare={onShareRecommendation}
                />
              ) : (
                <div className="reco-deck-empty">На сегодня всё — загляните позже</div>
              )}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="mobile-reco-overlay mobile-reco-overlay--v2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <button className="mobile-reco-close" type="button" aria-label="Закрыть" onClick={onClose}>
              <img src={assets.group12021Icon} alt="" />
            </button>

            <div className="reco-mobile-deck">
              {stackedCards
                .slice()
                .reverse()
                .map((card, i) => (
                  <div key={card.instanceId} className={`reco-mobile-stack reco-mobile-stack--${stackedCards.length - i}`}>
                    <StackedPreview card={card} depth={stackedCards.length - i} />
                  </div>
                ))}

              {topCard ? (
                <MobileTopCard
                  key={topCard.instanceId}
                  card={topCard}
                  canDismiss={canDismiss}
                  dismissDirection={dismissDirection}
                  exitTarget={exitTarget}
                  onDismissSwipe={onDismissTopCard}
                  onExitComplete={onTopCardExitComplete}
                  likedRecommendations={likedRecommendations}
                  onToggleLike={onToggleRecommendationLike}
                  onOpen={onOpenRecommendation}
                  onShare={onShareRecommendation}
                  stackIndex={totalCount - stackedCards.length - 1}
                  stackTotal={Math.max(1, totalCount)}
                />
              ) : (
                <p className="reco-mobile-empty">Карточки закончились</p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
