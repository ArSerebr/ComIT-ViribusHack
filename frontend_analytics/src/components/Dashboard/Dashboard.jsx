import { useQuery } from "@tanstack/react-query";
import { fetchUniversityDashboard } from "../../api/analyticsApi";
import { MetricCard } from "../MetricCard/MetricCard";
import { ExportButtons } from "../ExportButtons/ExportButtons";

export function Dashboard({ universityId }) {
  const { data: dashboard, isLoading, error } = useQuery({
    queryKey: ["analytics", "dashboard", universityId],
    queryFn: () => fetchUniversityDashboard(universityId),
    enabled: !!universityId,
  });

  if (!universityId) {
    return (
      <div className="dashboard dashboard--empty">
        Выберите университет для просмотра аналитики.
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="dashboard dashboard--loading">
        Загрузка дашборда…
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard dashboard--error">
        Ошибка: {error.message}
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="dashboard dashboard--error">
        Университет не найден.
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h2 className="dashboard__title">{dashboard.universityName}</h2>
      </header>

      <div className="dashboard__metrics">
        <MetricCard
          title="Зарегистрированные студенты"
          value={dashboard.studentsCount}
          icon="👥"
        />
        <MetricCard
          title="Участие в мероприятиях"
          value={dashboard.eventParticipationsCount}
          icon="📅"
        />
        <MetricCard
          title="Заявки на вступление в проекты"
          value={dashboard.joinRequestsCount}
          icon="📋"
        />
        <MetricCard
          title="Проекты студентов"
          value={dashboard.projectsCount}
          icon="📁"
        />
        <MetricCard
          title="Статьи студентов"
          value={dashboard.articlesCount}
          icon="📄"
        />
        {dashboard.interestsCount != null && dashboard.interestsCount > 0 && (
          <MetricCard
            title="Интересы"
            value={dashboard.interestsCount}
            icon="⭐"
          />
        )}
      </div>

      <ExportButtons universityId={universityId} />
    </div>
  );
}
