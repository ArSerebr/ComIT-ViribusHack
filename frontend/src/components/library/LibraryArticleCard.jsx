import { motion } from "framer-motion";

export function LibraryArticleCard({ item, delay = 0, onOpen }) {
  const handleOpen = () => {
    onOpen?.(item);
  };

  return (
    <motion.article
      className="glass-card library-article-card"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.32 }}
    >
      <button type="button" className="library-article-hit" aria-label={`Открыть статью ${item.title}`} onClick={handleOpen} />
      <div className="library-article-tags">
        {item.tags.map((tag) => (
          <span key={tag.id} className={`library-article-tag library-article-tag-${tag.tone}`}>
            <span className="library-article-tag-dot" aria-hidden="true" />
            {tag.label}
          </span>
        ))}
      </div>

      <h3 className="library-article-title">{item.title}</h3>
      <p className="library-article-description">{item.description}</p>

      <div className="library-article-footer">
        <div className="library-article-author">
          <img src={item.authorAvatarUrl} alt="" className="library-article-author-avatar" />
          <span className="library-article-author-name">{item.authorName}</span>
        </div>

        <button type="button" className="library-article-read-btn" onClick={handleOpen}>
          Читать
        </button>
      </div>
    </motion.article>
  );
}
