import { motion } from "framer-motion";
import { assets } from "../../assets";

function NotificationsBrandIcon() {
  return (
    <span className="notify-popover-brand-icon" aria-hidden="true">
      <img src={assets.bellIcon} alt="" />
    </span>
  );
}

function InviteNotificationCard({ item, onOpenNotification }) {
  return (
    <article className="notify-card notify-card-invite">
      <div className="notify-card-copy">
        <p className="notify-card-title">{item.title}</p>
        {item.unread ? <span className="notify-card-unread" aria-hidden="true" /> : null}
      </div>

      <div className="notify-card-footer">
        <div className="notify-card-meta">
          <div className="notify-card-author">
            <span>{item.authorLabel}</span>
            <strong>{item.authorName}</strong>
          </div>

          <button
            className="notify-card-open"
            type="button"
            aria-label={`Открыть уведомление ${item.title}`}
            onClick={() => onOpenNotification(item)}
          >
            <span className="notify-card-open-arrow" aria-hidden="true" />
          </button>
        </div>

        <div className="notify-card-datetime">
          <strong>{item.dateLabel}</strong>
          <span>{item.dateCaption}</span>
        </div>
      </div>
    </article>
  );
}

function ArticleNotificationCard({ item, onOpenNotification }) {
  return (
    <article className="notify-card notify-card-article">
      <div className="notify-card-copy">
        <p className="notify-card-title">{item.title}</p>
        <strong className="notify-card-accent">{item.accentText}</strong>
      </div>

      <div className="notify-card-footer">
        <button className="notify-card-read-btn" type="button" onClick={() => onOpenNotification(item)}>
          {item.ctaLabel}
        </button>

        <div className="notify-card-datetime">
          <strong>{item.dateLabel}</strong>
          <span>{item.dateCaption}</span>
        </div>
      </div>
    </article>
  );
}

export function NotificationsPopover({ items, onClose, onOpenNotification }) {
  return (
    <motion.section
      className="notifications-popover"
      initial={{ opacity: 0, y: -12, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -12, scale: 0.96 }}
      transition={{ duration: 0.22, ease: "easeOut" }}
    >
      <div className="notify-popover-head">
        <div className="notify-popover-title-wrap">
          <NotificationsBrandIcon />
          <h2>Уведомления</h2>
        </div>

        <button className="notify-popover-close" type="button" aria-label="Закрыть уведомления" onClick={onClose}>
          <img src={assets.group12021Icon} alt="" />
        </button>
      </div>

      <div className="notify-popover-list">
        {items.map((item) =>
          item.type === "invite" ? (
            <InviteNotificationCard key={item.id} item={item} onOpenNotification={onOpenNotification} />
          ) : (
            <ArticleNotificationCard key={item.id} item={item} onOpenNotification={onOpenNotification} />
          ),
        )}
      </div>
    </motion.section>
  );
}
