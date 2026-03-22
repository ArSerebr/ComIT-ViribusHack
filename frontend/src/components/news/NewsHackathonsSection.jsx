import { assets } from "../../assets";

function formatDateRange(startDate, endDate) {
  if (!startDate && !endDate) {
    return null;
  }
  const opts = { day: "numeric", month: "short", year: "numeric" };
  const fmt = new Intl.DateTimeFormat("ru-RU", opts);
  try {
    if (startDate && endDate && startDate !== endDate) {
      return `${fmt.format(new Date(startDate))} — ${fmt.format(new Date(endDate))}`;
    }
    const d = startDate || endDate;
    return fmt.format(new Date(d));
  } catch {
    return startDate || endDate;
  }
}

function HackathonCard({ item }) {
  const when = formatDateRange(item.start_date, item.end_date);
  const place =
    item.is_online ? "Онлайн" : item.location?.trim() || null;
  const meta = [when, place].filter(Boolean).join(" · ");
  const href = item.url?.trim() || null;
  const desc = item.description?.trim() || null;
  const img = item.image_url?.trim() || null;

  const inner = (
    <>
      {img ? (
        <div className="news-hackathon-card-image-wrap">
          <img src={img} alt="" className="news-hackathon-card-image" loading="lazy" />
        </div>
      ) : (
        <div className="news-hackathon-card-image-wrap news-hackathon-card-image-wrap--placeholder" aria-hidden>
          <img src={assets.posterHackathon} alt="" className="news-hackathon-card-image" />
        </div>
      )}
      <div className="news-hackathon-card-body">
        <h3 className="news-hackathon-card-title">{item.title}</h3>
        {meta ? <p className="news-hackathon-card-meta">{meta}</p> : null}
        {item.organizer ? <p className="news-hackathon-card-org">{item.organizer}</p> : null}
        {desc ? <p className="news-hackathon-card-desc">{desc}</p> : null}
        {href ? (
          <span className="news-hackathon-card-cta">Перейти к событию</span>
        ) : null}
      </div>
    </>
  );

  if (href) {
    return (
      <a
        className="news-hackathon-card"
        href={href}
        target="_blank"
        rel="noopener noreferrer"
      >
        {inner}
      </a>
    );
  }

  return <article className="news-hackathon-card news-hackathon-card--static">{inner}</article>;
}

export function NewsHackathonsSection({ items, isLoading, isError }) {
  return (
    <section className="news-hackathons-section" aria-labelledby="news-hackathons-heading">
      <div className="news-hackathons-head">
        <h2 id="news-hackathons-heading" className="news-hackathons-title">
          Хакатоны
        </h2>
        <p className="news-hackathons-caption">
          Показаны только предстоящие и идущие события (по датам UTC). Источники: hacklist, cups.online и др.
        </p>
      </div>

      {isLoading ? (
        <div className="news-hackathons-loading" role="status" aria-live="polite">
          <span className="loading-spinner" aria-hidden />
          Загружаем хакатоны…
        </div>
      ) : null}

      {!isLoading && isError ? (
        <p className="news-hackathons-fallback" role="status">
          Не удалось загрузить список хакатонов. Попробуйте обновить страницу позже.
        </p>
      ) : null}

      {!isLoading && !isError && items.length === 0 ? (
        <p className="news-hackathons-empty" role="status">
          Пока нет записей в базе. После синхронизации парсера здесь появятся актуальные хакатоны.
        </p>
      ) : null}

      {!isLoading && !isError && items.length > 0 ? (
        <div className="news-hackathons-grid">
          {items.map((item) => (
            <HackathonCard key={item.id} item={item} />
          ))}
        </div>
      ) : null}
    </section>
  );
}
