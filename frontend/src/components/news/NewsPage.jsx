import { assets } from "../../assets";
import { FeaturedNewsCard } from "./FeaturedNewsCard";
import { NewsMiniCard } from "./NewsMiniCard";

function buildNewsRows(miniNewsItems, featuredNewsItems) {
  const rows = featuredNewsItems.map((featuredItem, rowIndex) => ({
    id: `row-${featuredItem.id}-${rowIndex}`,
    featuredItem,
    miniItems: miniNewsItems.slice(rowIndex * 2, rowIndex * 2 + 2)
  }));

  const remainingMiniItems = miniNewsItems.slice(featuredNewsItems.length * 2);
  return { rows, remainingMiniItems };
}

export function NewsPage({
  miniNewsItems,
  featuredNewsItems,
  likedNews,
  onToggleNewsLike,
  onOpenMiniNews,
  onParticipateInEvent,
  onBack,
  isLoading = false,
  showOfflineFallbackNotice = false
}) {
  const { rows, remainingMiniItems } = buildNewsRows(miniNewsItems, featuredNewsItems);

  return (
    <section className="news-page">
      <div className="news-page-head">
        <button className="news-back-btn" type="button" aria-label="Назад на главную" onClick={onBack}>
          <img src={assets.arrowSmallLeftIcon} alt="" />
        </button>
        <h1 className="news-page-title">Новости и ивенты</h1>
      </div>

      {isLoading ? (
        <div className="api-banner api-banner--loading" role="status" aria-live="polite">
          <span className="loading-spinner" aria-hidden />
          Загрузка новостей…
        </div>
      ) : null}
      {showOfflineFallbackNotice ? (
        <p className="api-banner api-banner--warn" role="status">
          Не удалось получить данные с сервера — показаны демо-материалы из приложения.
        </p>
      ) : null}

      <div className="news-page-rows">
        {rows.map((row, rowIndex) => (
          <div className="news-page-row" key={row.id}>
            <div className="news-row-mini-grid">
              {row.miniItems.map((item, miniIndex) => (
                <NewsMiniCard
                  key={item.id}
                  item={item}
                  className="news-page-mini-card"
                  isLiked={Boolean(likedNews[item.id])}
                  onToggleLike={onToggleNewsLike}
                  onOpen={onOpenMiniNews}
                  delay={0.08 + rowIndex * 0.08 + miniIndex * 0.05}
                />
              ))}
            </div>

            <FeaturedNewsCard
              item={row.featuredItem}
              className="news-page-featured-card"
              onParticipate={onParticipateInEvent}
              delay={0.16 + rowIndex * 0.09}
            />
          </div>
        ))}

        {remainingMiniItems.length ? (
          <div className="news-row-mini-grid news-row-mini-grid-tail">
            {remainingMiniItems.map((item, index) => (
              <NewsMiniCard
                key={item.id}
                item={item}
                className="news-page-mini-card"
                isLiked={Boolean(likedNews[item.id])}
                onToggleLike={onToggleNewsLike}
                onOpen={onOpenMiniNews}
                delay={0.16 + rows.length * 0.08 + index * 0.05}
              />
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
}
