import { motion } from "framer-motion";

export function FeaturedNewsCard({ item, onParticipate, delay = 0, className = "" }) {
  const handleOpen = () => {
    onParticipate(item);
  };

  const cardClassName = ["glass-card featured-news-card", className].filter(Boolean).join(" ");

  return (
    <motion.article
      className={cardClassName}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.38 }}
      onClick={handleOpen}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === "Enter") {
          handleOpen();
        }
      }}
    >
      <img src={item.imageUrl} alt={item.title} className="featured-news-image" />
      <div className="featured-news-overlay" />
      <div className="featured-news-content">
        <h2>{item.title}</h2>
        <p className="featured-news-subtitle">{item.subtitle}</p>
        <p className="featured-news-description">{item.description}</p>
        <button
          className="featured-news-cta"
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            handleOpen();
          }}
        >
          + {item.ctaLabel}
        </button>
      </div>
    </motion.article>
  );
}
