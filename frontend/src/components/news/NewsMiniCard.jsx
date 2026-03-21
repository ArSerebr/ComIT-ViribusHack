import { AnimatePresence, motion } from "framer-motion";
import { assets } from "../../assets";

const NEWS_LINK_BUTTON_VARIANTS = {
  rest: {
    gap: 10
  },
  hover: {
    gap: 14
  },
  tap: {
    gap: 12
  }
};

const NEWS_LINK_LABEL_VARIANTS = {
  rest: {
    x: 0,
    opacity: 0.94
  },
  hover: {
    x: 4,
    opacity: 1
  },
  tap: {
    x: 2,
    opacity: 1
  }
};

const NEWS_LINK_ARROW_VARIANTS = {
  rest: {
    x: 0,
    scale: 1,
    rotate: 0
  },
  hover: {
    x: 8,
    scale: 1.08,
    rotate: -8
  },
  tap: {
    x: 4,
    scale: 0.98,
    rotate: -4
  }
};

const NEWS_LINK_SHINE_VARIANTS = {
  rest: {
    opacity: 0.18,
    x: "-28%"
  },
  hover: {
    opacity: 0.95,
    x: "28%"
  },
  tap: {
    opacity: 0.72,
    x: "14%"
  }
};

export function NewsMiniCard({
  item,
  isLiked,
  onToggleLike,
  onOpen,
  className = "",
  delay = 0,
  showLike = true
}) {
  const cardClassName = ["glass-card news-card", className].filter(Boolean).join(" ");

  const handleOpen = () => {
    onOpen(item);
  };

  return (
    <motion.article
      className={cardClassName}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.36 }}
      onClick={handleOpen}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === "Enter") {
          handleOpen();
        }
      }}
    >
      <div className="news-image-wrap">
        <img src={item.imageUrl} alt={item.title} draggable="false" />
      </div>
      <p className="news-text">{item.title}</p>
      {showLike ? (
        <motion.button
          className={`news-like-btn ${isLiked ? "news-like-btn-active" : ""}`}
          type="button"
          aria-label="Лайк новости"
          onClick={(event) => {
            event.stopPropagation();
            onToggleLike(item.id);
          }}
          whileHover={{ y: -3, scale: 1.04 }}
          whileTap={{ scale: 0.92 }}
          animate={isLiked ? { y: [0, -2, 0], scale: [1, 1.08, 1] } : { y: 0, scale: 1 }}
          transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
        >
          <AnimatePresence initial={false}>
            {isLiked ? (
              <motion.span
                key="news-like-burst"
                className="news-like-burst"
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
            className={`news-like-icon ${isLiked ? "news-like-icon-active" : ""}`}
            animate={isLiked ? { scale: [1, 1.18, 1], rotate: [0, -10, 0] } : { scale: 0.94, rotate: 0 }}
            transition={{ duration: 0.34, ease: [0.22, 1, 0.36, 1] }}
          />
        </motion.button>
      ) : null}
      <motion.button
        className="news-link-btn"
        type="button"
        initial="rest"
        animate="rest"
        whileHover="hover"
        whileTap="tap"
        variants={NEWS_LINK_BUTTON_VARIANTS}
        transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
        onClick={(event) => {
          event.stopPropagation();
          handleOpen();
        }}
      >
        <motion.span className="news-link-btn-shine" variants={NEWS_LINK_SHINE_VARIANTS} transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }} />
        <motion.span className="news-link-label" variants={NEWS_LINK_LABEL_VARIANTS} transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}>
          Подробнее
        </motion.span>
        <motion.span className="news-link-arrow-wrap" variants={NEWS_LINK_ARROW_VARIANTS} transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}>
          <img src={assets.arrow16Icon} alt="" />
        </motion.span>
      </motion.button>
    </motion.article>
  );
}
