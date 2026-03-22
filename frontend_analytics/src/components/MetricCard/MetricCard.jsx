export function MetricCard({ title, value, icon }) {
  return (
    <div className="metric-card">
      {icon && <span className="metric-card__icon">{icon}</span>}
      <div className="metric-card__content">
        <span className="metric-card__value">{value}</span>
        <span className="metric-card__title">{title}</span>
      </div>
    </div>
  );
}
