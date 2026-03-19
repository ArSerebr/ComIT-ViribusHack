import { motion } from "framer-motion";
import { assets } from "../../assets";

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
        <img src={item.imageUrl} alt={item.title} />
      </div>
      <p className="news-text">{item.title}</p>
      {showLike ? (
        <button
          className="news-like-btn"
          type="button"
          aria-label="Лайк новости"
          onClick={(event) => {
            event.stopPropagation();
            onToggleLike(item.id);
          }}
        >
          <img src={isLiked ? assets.heartFilledIcon : assets.heartOutlineIcon} alt="" />
        </button>
      ) : null}
      <button
        className="news-link-btn"
        type="button"
        onClick={(event) => {
          event.stopPropagation();
          handleOpen();
        }}
      >
        Подробнее
        <img src={assets.arrow16Icon} alt="" />
      </button>
    </motion.article>
  );
}
