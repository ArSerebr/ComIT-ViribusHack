import { useQuery } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import { assets } from "../../assets";
import { formatOpenApiError, fetchProjectById, postWorkPlanAssign, postWorkPlanGenerate } from "../../api/publicApi";
import { pollTask } from "../../api/pulseApi";

const POLL_MS = 1200;
const PLAN_TIMEOUT_MS = 180_000;

export function ProjectTasksPage({ projectId, sessionToken, onBack, onOpenProjectDetails }) {
  const [planSummary, setPlanSummary] = useState("");
  const [normalizedConcept, setNormalizedConcept] = useState("");
  const [tasks, setTasks] = useState([]);
  const [assignments, setAssignments] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [deadlineInput, setDeadlineInput] = useState("");

  const projectQuery = useQuery({
    queryKey: ["projects", "detail", projectId],
    queryFn: () => fetchProjectById(projectId),
    enabled: Boolean(projectId),
    staleTime: 30_000
  });

  const project = projectQuery.data;

  const pollUntilReady = useCallback(
    async (taskId) => {
      const end = Date.now() + PLAN_TIMEOUT_MS;
      while (Date.now() < end) {
        await new Promise((r) => setTimeout(r, POLL_MS));
        const data = await pollTask(sessionToken, taskId);
        const st = (data.status || "").toUpperCase();
        if (st === "READY" && data.result) {
          return data.result;
        }
        if (st === "FAILED") {
          throw new Error(data.result?.error || "Генерация плана не удалась");
        }
      }
      throw new Error("Превышено время ожидания генерации плана");
    },
    [sessionToken]
  );

  const handleGenerate = async () => {
    if (!sessionToken?.trim()) {
      setError("Войдите в аккаунт, чтобы сгенерировать план.");
      return;
    }
    setError(null);
    setBusy(true);
    setAssignments(null);
    try {
      const { task_id: taskId } = await postWorkPlanGenerate(
        sessionToken,
        projectId,
        deadlineInput.trim() || null
      );
      const result = await pollUntilReady(taskId);
      const content = result.content || {};
      const list = content.work_plan_tasks || [];
      setPlanSummary(content.plan_summary || "");
      setNormalizedConcept(content.normalized_concept || "");
      setTasks(Array.isArray(list) ? list : []);
    } catch (e) {
      setError(formatOpenApiError(e) || String(e));
    } finally {
      setBusy(false);
    }
  };

  const handleAssign = async () => {
    if (!sessionToken?.trim()) {
      setError("Войдите в аккаунт.");
      return;
    }
    if (!tasks.length) {
      setError("Сначала сгенерируйте план задач.");
      return;
    }
    setError(null);
    setBusy(true);
    try {
      const payload = await postWorkPlanAssign(sessionToken, projectId, tasks);
      setAssignments(payload);
    } catch (e) {
      setError(formatOpenApiError(e) || String(e));
    } finally {
      setBusy(false);
    }
  };

  if (projectQuery.isLoading) {
    return (
      <section className="project-tasks-page">
        <div className="library-page-head">
          <button type="button" className="news-back-btn" aria-label="Назад" onClick={onBack}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <p className="page-title">Загрузка проекта…</p>
        </div>
      </section>
    );
  }

  if (projectQuery.isError || !project) {
    return (
      <section className="project-tasks-page">
        <div className="library-page-head">
          <button type="button" className="news-back-btn" aria-label="Назад" onClick={onBack}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <p className="page-title">Проект не найден.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="project-tasks-page">
      <div className="project-details-head">
        <div className="project-details-heading">
          <button type="button" className="news-back-btn project-details-back-btn" aria-label="Назад" onClick={onBack}>
            <img src={assets.arrowSmallLeftIcon} alt="" />
          </button>
          <div className="project-details-title-block">
            <h1 className="project-details-title">Задачи: {project.title}</h1>
            <p className="project-details-byline">
              Идея → план → распределение по команде
              {onOpenProjectDetails ? (
                <>
                  {" · "}
                  <button type="button" className="project-tasks-link-inline" onClick={() => onOpenProjectDetails(project)}>
                    Карточка проекта
                  </button>
                </>
              ) : null}
            </p>
          </div>
        </div>
      </div>

      <div className="project-tasks-layout glass-card">
        <p className="project-tasks-lead">{project.description}</p>

        <div className="project-tasks-controls">
          <label className="project-tasks-deadline-label">
            Крайний срок проекта (опционально)
            <input
              type="date"
              className="project-tasks-deadline-input"
              value={deadlineInput}
              onChange={(e) => setDeadlineInput(e.target.value)}
              disabled={busy}
            />
          </label>
          <div className="project-tasks-actions">
            <button
              type="button"
              className="projects-hub-create-btn"
              disabled={busy}
              onClick={() => void handleGenerate()}
            >
              {busy ? "Подождите…" : "Сгенерировать план"}
            </button>
            <button
              type="button"
              className="project-details-team-action"
              disabled={busy || !tasks.length}
              onClick={() => void handleAssign()}
            >
              Распределить по команде
            </button>
          </div>
        </div>

        {error ? <p className="project-tasks-error">{error}</p> : null}

        {normalizedConcept ? (
          <div className="project-tasks-block">
            <h2 className="project-tasks-h2">Концепция</h2>
            <p className="project-tasks-concept">{normalizedConcept}</p>
          </div>
        ) : null}

        {planSummary ? (
          <div className="project-tasks-block">
            <h2 className="project-tasks-h2">Резюме плана</h2>
            <p>{planSummary}</p>
          </div>
        ) : null}

        {tasks.length > 0 ? (
          <div className="project-tasks-block">
            <h2 className="project-tasks-h2">Задачи ({tasks.length})</h2>
            <ul className="project-tasks-list">
              {tasks.map((t) => (
                <li key={t.id} className="project-tasks-list-item">
                  <strong>{t.title}</strong>
                  <span className="project-tasks-meta">
                    {t.deadline_iso ? `до ${t.deadline_iso}` : ""}
                    {t.estimated_hours != null ? ` · ~${t.estimated_hours} ч` : ""}
                    {t.category ? ` · ${t.category}` : ""}
                  </span>
                  <p className="project-tasks-desc">{t.description}</p>
                  <p className="project-tasks-skills">Навыки: {(t.required_skills || []).join(", ") || "—"}</p>
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {assignments?.assignments?.length ? (
          <div className="project-tasks-block">
            <h2 className="project-tasks-h2">Назначения</h2>
            <p className="project-tasks-coverage">
              Покрытие команды: {assignments.team_coverage?.assigned_members ?? "—"} /{" "}
              {assignments.team_coverage?.total_members ?? "—"}
            </p>
            <ul className="project-tasks-assign-list">
              {assignments.assignments.map((a) => (
                <li key={a.task_id} className="project-tasks-assign-item">
                  <div className="project-tasks-assign-head">
                    <strong>{a.task_title}</strong>
                    <span className="project-tasks-meta">
                      {a.deadline_iso ? `до ${a.deadline_iso}` : ""}
                    </span>
                  </div>
                  {a.assigned_to?.map((p) => (
                    <div key={`${a.task_id}-${p.member_id}-${p.responsibility}`} className="project-tasks-assignee">
                      <span>
                        {p.name} ({p.role}) — {p.responsibility}
                      </span>
                      <span className="project-tasks-score">
                        score {p.score_breakdown?.total?.toFixed?.(3) ?? p.score_breakdown?.total}
                      </span>
                      <p className="project-tasks-why">{p.why}</p>
                    </div>
                  ))}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </section>
  );
}
