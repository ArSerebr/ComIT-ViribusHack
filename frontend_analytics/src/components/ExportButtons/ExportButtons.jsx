import { useState } from "react";
import { downloadExport } from "../../api/analyticsApi";

const EXPORTS = [
  { type: "students", label: "Студенты", filename: "students.csv" },
  { type: "participation", label: "Участие в мероприятиях", filename: "participation.csv" },
  { type: "projects", label: "Проекты", filename: "projects.csv" },
  { type: "articles", label: "Статьи", filename: "articles.csv" },
  { type: "join-requests", label: "Заявки в проекты", filename: "join_requests.csv" },
];

export function ExportButtons({ universityId }) {
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState(null);

  const handleExport = async (type, filename) => {
    if (!universityId) return;
    setLoading(type);
    setError(null);
    try {
      await downloadExport(universityId, type, filename);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(null);
    }
  };

  if (!universityId) return null;

  return (
    <div className="export-buttons">
      <h3 className="export-buttons__title">Выгрузка CSV</h3>
      {error && <div className="export-buttons__error">{error}</div>}
      <div className="export-buttons__grid">
        {EXPORTS.map(({ type, label, filename }) => (
          <button
            key={type}
            type="button"
            className="export-buttons__btn"
            onClick={() => handleExport(type, filename)}
            disabled={loading !== null}
          >
            {loading === type ? "Скачивание…" : label}
          </button>
        ))}
      </div>
    </div>
  );
}
