import { useQuery } from "@tanstack/react-query";
import { fetchUniversities } from "../../api/analyticsApi";

export function UniversitySelector({ value, onChange, disabled }) {
  const { data: universities = [], isLoading, error } = useQuery({
    queryKey: ["analytics", "universities"],
    queryFn: fetchUniversities,
  });

  if (isLoading) {
    return (
      <div className="university-selector university-selector--loading">
        Загрузка университетов…
      </div>
    );
  }

  if (error) {
    return (
      <div className="university-selector university-selector--error">
        Ошибка загрузки: {error.message}
      </div>
    );
  }

  return (
    <div className="university-selector">
      <label htmlFor="university-select" className="university-selector__label">
        Выберите университет
      </label>
      <select
        id="university-select"
        className="university-selector__select"
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value || null)}
        disabled={disabled}
      >
        <option value="">— Выберите —</option>
        {universities.map((u) => (
          <option key={u.id} value={u.id}>
            {u.name} ({u.studentsCount} студентов)
          </option>
        ))}
      </select>
    </div>
  );
}
