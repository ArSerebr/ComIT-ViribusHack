from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Any, Dict, List, Protocol

from app.modules.projects.task_assignment.gigachat_embeddings import GigaChatEmbeddingsClient
from app.modules.projects.task_assignment.hash_embeddings import HashEmbeddingProvider


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class SupportsEmbed(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


def create_embedding_provider() -> SupportsEmbed:
    try:
        return GigaChatEmbeddingsClient()
    except RuntimeError:
        return HashEmbeddingProvider(dim=256)


def cosine_similarity(left: List[float], right: List[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right))


def _as_str_list(val: Any) -> List[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [val.strip()] if val.strip() else []
    if isinstance(val, list):
        return [str(s).strip() for s in val if str(s).strip()]
    return []


def normalize_member(raw: Dict[str, Any]) -> Dict[str, Any]:
    mid = raw.get("id") or raw.get("member_id") or raw.get("student_id")
    if not mid:
        mid = f"m-{uuid.uuid4().hex[:10]}"
    skills = [s.lower() for s in _as_str_list(raw.get("skills"))]
    secondary = [s.lower() for s in _as_str_list(raw.get("secondary_skills"))]
    interest_labels = _as_str_list(raw.get("interest_labels"))
    for label in interest_labels:
        low = label.lower()
        if low not in skills:
            skills.append(low)
    return {
        "id": str(mid),
        "name": str(raw.get("name") or "Участник"),
        "role": str(raw.get("role") or "Участник"),
        "bio": str(raw.get("bio") or raw.get("lastTask") or ""),
        "skills": skills or ["general"],
        "secondary_skills": secondary,
        "availability_hours_per_week": int(raw.get("availability_hours_per_week") or 20),
        "current_load_hours": int(raw.get("current_load_hours") or 0),
        "max_parallel_tasks": int(raw.get("max_parallel_tasks") or 4),
    }


def normalize_task_dict(raw: Dict[str, Any]) -> Dict[str, Any]:
    tid = raw.get("id")
    if not tid:
        tid = f"task-{uuid.uuid4().hex[:8]}"
    skills = _as_str_list(raw.get("required_skills"))
    if not skills:
        skills = ["general"]
    cat = str(raw.get("category") or "other").strip().lower()
    diff = str(raw.get("difficulty") or "medium").strip().lower()
    if diff not in {"low", "medium", "high"}:
        diff = "medium"
    prio = str(raw.get("priority") or "should_have").strip().lower()
    if prio not in {"must_have", "should_have", "nice_to_have"}:
        prio = "should_have"
    try:
        hours = int(raw.get("estimated_hours") or 8)
    except (TypeError, ValueError):
        hours = 8
    hours = max(1, min(hours, 200))
    deadline = raw.get("deadline_iso") or raw.get("due_date") or raw.get("deadline") or ""
    deadline = str(deadline).strip() if deadline else ""
    return {
        "id": str(tid),
        "title": str(raw.get("title") or "Задача").strip(),
        "description": str(raw.get("description") or raw.get("title") or "").strip(),
        "required_skills": skills,
        "category": cat,
        "difficulty": diff,
        "estimated_hours": hours,
        "priority": prio,
        "deadline_iso": deadline,
    }


def textify_member(member: Dict[str, Any]) -> str:
    return " ".join(
        [
            member["name"],
            member["role"],
            member["bio"],
            " ".join(member["skills"]),
            " ".join(member["secondary_skills"]),
        ]
    )


def textify_task(project: Dict[str, Any], task: Dict[str, Any]) -> str:
    parts = [
        project.get("title", ""),
        project.get("description", ""),
        task.get("title", ""),
        task.get("description", ""),
        " ".join(task.get("required_skills", [])),
        task.get("category", ""),
        task.get("difficulty", ""),
        task.get("deadline_iso", ""),
    ]
    return " ".join(str(p) for p in parts if p)


ROLE_HINTS: Dict[str, List[str]] = {
    "product": ["Product Manager", "Business Analyst", "Project Coordinator", "Продакт", "Аналитик"],
    "design": ["UX/UI Designer", "Product Designer", "дизайнер", "UX/UI"],
    "frontend": ["Frontend Engineer", "Fullstack Engineer", "Frontend", "фронтенд"],
    "backend": ["Backend Engineer", "Backend / Security", "Fullstack Engineer", "бэкенд", "Backend"],
    "mobile": ["Mobile Engineer", "мобильная разработка"],
    "devops": ["DevOps Engineer", "DevOps"],
    "qa": ["QA Engineer", "QA Automation Engineer", "тестирование", "QA"],
    "analytics": ["Data Analyst", "Growth Analyst", "Product Manager", "аналитик"],
    "ml": ["Data Scientist", "ML", "машинное обучение"],
    "other": [],
}


@dataclass
class CandidateScore:
    member: Dict[str, Any]
    total_score: float
    semantic_score: float
    skills_score: float
    role_score: float
    workload_score: float
    overlap_skills: List[str]
    remaining_capacity: int


class TaskAssignmentModel:
    MAX_ASSIGNEES_PER_TASK = 2
    COLLABORATOR_LOAD_RATIO = 0.5

    def __init__(
        self,
        encoder: SupportsEmbed | None = None,
        *,
        projects: List[Dict[str, Any]] | None = None,
        team: List[Dict[str, Any]] | None = None,
    ) -> None:
        self.encoder = encoder or create_embedding_provider()
        self._file_projects = projects
        self._file_team = team
        self.projects = projects or []
        self.team: List[Dict[str, Any]] = []
        self.member_embeddings: Dict[str, List[float]] = {}
        self.project_index: Dict[str, Dict[str, Any]] = (
            {p["id"]: p for p in self.projects} if self.projects else {}
        )

    @classmethod
    def from_json_files(cls, projects_path: Path, team_path: Path) -> TaskAssignmentModel:
        projects = load_json(projects_path)
        team = load_json(team_path)
        if not isinstance(projects, list):
            raise ValueError("projects.json must be a list")
        if not isinstance(team, list):
            raise ValueError("team.json must be a list")
        inst = cls(encoder=create_embedding_provider(), projects=projects, team=team)
        inst.team = [normalize_member(m) for m in team]
        inst._rebuild_member_embeddings()
        inst.project_index = {p["id"]: p for p in projects}
        return inst

    def _rebuild_member_embeddings(self) -> None:
        member_texts = [textify_member(m) for m in self.team]
        member_vectors = self.encoder.embed_texts(member_texts)
        self.member_embeddings = {
            member["id"]: member_vectors[i] for i, member in enumerate(self.team)
        }

    def assign_project_data(
        self,
        project: Dict[str, Any],
        team: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Назначение задач только на переданный список участников."""
        norm_team = [normalize_member(m) for m in team]
        if not norm_team:
            raise ValueError("team must contain at least one member")
        raw_tasks = project.get("tasks")
        if not isinstance(raw_tasks, list) or not raw_tasks:
            raise ValueError("project.tasks must be a non-empty list")
        tasks_norm = [normalize_task_dict(t) for t in raw_tasks if isinstance(t, dict)]

        prev_team = self.team
        prev_emb = self.member_embeddings
        self.team = norm_team
        self._rebuild_member_embeddings()

        proj_for_assign = {
            "id": str(project.get("id") or "project"),
            "title": str(project.get("title") or ""),
            "description": str(project.get("description") or ""),
            "domain": str(project.get("domain") or "general"),
            "tasks": tasks_norm,
        }
        try:
            result = self._assign_core(proj_for_assign)
        finally:
            self.team = prev_team
            self.member_embeddings = prev_emb

        result["project_domain"] = proj_for_assign["domain"]
        return result

    def assign_project(self, project_id: str) -> Dict[str, Any]:
        if not self._file_projects or not self._file_team:
            raise ValueError("from_json_files() required for assign_project(project_id)")
        project = self.project_index.get(project_id)
        if not project:
            raise ValueError(f"Project with id '{project_id}' not found")
        team = [normalize_member(m) for m in self._file_team]
        return self.assign_project_data(project, team)

    def _rank_candidates(
        self,
        task: Dict[str, Any],
        project: Dict[str, Any],
        assigned_hours: Dict[str, int],
        assigned_tasks: Dict[str, int],
        task_embedding: List[float],
    ) -> List[CandidateScore]:
        return sorted(
            [
                self._candidate_score(
                    task,
                    project,
                    member,
                    assigned_hours,
                    assigned_tasks,
                    task_embedding,
                )
                for member in self.team
            ],
            key=lambda item: item.total_score,
            reverse=True,
        )

    def _candidate_score(
        self,
        task: Dict[str, Any],
        project: Dict[str, Any],
        member: Dict[str, Any],
        assigned_hours: Dict[str, int],
        assigned_tasks: Dict[str, int],
        task_embedding: List[float],
    ) -> CandidateScore:
        member_embedding = self.member_embeddings[member["id"]]
        semantic_score = cosine_similarity(task_embedding, member_embedding)

        member_skill_pool = {s.lower() for s in member["skills"] + member["secondary_skills"]}
        required = task.get("required_skills", [])
        required_skills = [str(s).lower() for s in required]
        overlap_skills = [str(s) for s in required if str(s).lower() in member_skill_pool]
        skills_score = len(overlap_skills) / max(1, len(required_skills))

        preferred_roles = ROLE_HINTS.get(task["category"], [])
        role_score = 1.0 if member["role"] in preferred_roles else 0.2
        if preferred_roles:
            role_lower = member["role"].lower()
            if any(pr.lower() in role_lower or role_lower in pr.lower() for pr in preferred_roles):
                role_score = max(role_score, 0.85)

        max_capacity = max(1, member["availability_hours_per_week"] * 4)
        remaining_capacity = max_capacity - member["current_load_hours"] - assigned_hours[member["id"]]
        workload_ratio = max(0.0, min(1.0, remaining_capacity / max_capacity))
        mpt = max(1, member["max_parallel_tasks"])
        task_slots_left = mpt - assigned_tasks[member["id"]]
        parallel_ratio = max(0.0, min(1.0, task_slots_left / mpt))
        workload_score = (0.7 * workload_ratio) + (0.3 * parallel_ratio)

        total_score = (
            0.45 * semantic_score
            + 0.35 * skills_score
            + 0.12 * role_score
            + 0.08 * workload_score
        )

        if remaining_capacity < task["estimated_hours"]:
            total_score -= 0.15
        if assigned_tasks[member["id"]] >= member["max_parallel_tasks"]:
            total_score -= 0.12

        return CandidateScore(
            member=member,
            total_score=total_score,
            semantic_score=semantic_score,
            skills_score=skills_score,
            role_score=role_score,
            workload_score=workload_score,
            overlap_skills=overlap_skills,
            remaining_capacity=remaining_capacity,
        )

    def _build_assignee_payload(
        self,
        task: Dict[str, Any],
        candidate: CandidateScore,
        responsibility: str,
        extra_reason: str | None = None,
    ) -> Dict[str, Any]:
        return {
            "member_id": candidate.member["id"],
            "student_id": candidate.member["id"],
            "name": candidate.member["name"],
            "role": candidate.member["role"],
            "responsibility": responsibility,
            "score_breakdown": {
                "total": round(candidate.total_score, 4),
                "semantic_score": round(candidate.semantic_score, 4),
                "skills_score": round(candidate.skills_score, 4),
                "role_score": round(candidate.role_score, 4),
                "workload_score": round(candidate.workload_score, 4),
            },
            "why": self._build_explanation(task, candidate, responsibility, extra_reason),
        }

    def _apply_assignment_load(
        self,
        member_id: str,
        task_hours: int,
        assigned_hours: Dict[str, int],
        assigned_tasks: Dict[str, int],
        ratio: float,
    ) -> None:
        assigned_hours[member_id] += max(1, ceil(task_hours * ratio))
        assigned_tasks[member_id] += 1

    def _choose_task_for_unassigned_member(
        self,
        member: Dict[str, Any],
        project: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        task_embeddings: Dict[str, List[float]],
        task_assignments_by_id: Dict[str, Dict[str, Any]],
        assigned_hours: Dict[str, int],
        assigned_tasks: Dict[str, int],
    ) -> tuple[Dict[str, Any], CandidateScore] | None:
        best_option = None

        for task in tasks:
            assignment = task_assignments_by_id[task["id"]]
            if len(assignment["assigned_to"]) >= self.MAX_ASSIGNEES_PER_TASK:
                continue
            if any(item["member_id"] == member["id"] for item in assignment["assigned_to"]):
                continue

            candidate = self._candidate_score(
                task,
                project,
                member,
                assigned_hours,
                assigned_tasks,
                task_embeddings[task["id"]],
            )

            score = candidate.total_score
            if candidate.skills_score >= 0.66:
                score += 0.05
            if assignment["assigned_to"][0]["score_breakdown"]["total"] - candidate.total_score <= 0.08:
                score += 0.03

            if best_option is None or score > best_option[2]:
                best_option = (task, candidate, score)

        if best_option is None:
            return None
        return best_option[0], best_option[1]

    def _maybe_add_strong_collaborator(
        self,
        task: Dict[str, Any],
        project: Dict[str, Any],
        task_assignment: Dict[str, Any],
        task_embedding: List[float],
        assigned_hours: Dict[str, int],
        assigned_tasks: Dict[str, int],
        member_involvement: Dict[str, int],
    ) -> None:
        if len(task_assignment["assigned_to"]) >= self.MAX_ASSIGNEES_PER_TASK:
            return

        ranking = self._rank_candidates(
            task,
            project,
            assigned_hours,
            assigned_tasks,
            task_embedding,
        )
        primary = task_assignment["assigned_to"][0]
        primary_score = primary["score_breakdown"]["total"]

        for candidate in ranking:
            if candidate.member["id"] == primary["member_id"]:
                continue
            if member_involvement[candidate.member["id"]] == 0:
                continue
            if candidate.skills_score < 0.66:
                continue
            if primary_score - candidate.total_score > 0.06:
                continue

            self._apply_assignment_load(
                candidate.member["id"],
                task["estimated_hours"],
                assigned_hours,
                assigned_tasks,
                ratio=self.COLLABORATOR_LOAD_RATIO,
            )
            member_involvement[candidate.member["id"]] += 1
            task_assignment["assigned_to"].append(
                self._build_assignee_payload(
                    task,
                    candidate,
                    responsibility="collaborator",
                    extra_reason="добавлен как соисполнитель, потому что его профиль почти не уступает основному исполнителю",
                )
            )
            break

    def _assign_core(self, project: Dict[str, Any]) -> Dict[str, Any]:
        assigned_hours = {member["id"]: 0 for member in self.team}
        assigned_tasks = {member["id"]: 0 for member in self.team}
        member_involvement = {member["id"]: 0 for member in self.team}
        task_assignments: List[Dict[str, Any]] = []
        p_tasks: List[Dict[str, Any]] = project["tasks"]
        task_texts = [textify_task(project, task) for task in p_tasks]
        task_vectors = self.encoder.embed_texts(task_texts)
        task_embeddings = {task["id"]: task_vectors[i] for i, task in enumerate(p_tasks)}

        tasks = sorted(
            p_tasks,
            key=lambda t: (
                {"must_have": 0, "should_have": 1, "nice_to_have": 2}[t["priority"]],
                {"high": 0, "medium": 1, "low": 2}[t["difficulty"]],
                -t["estimated_hours"],
            ),
        )

        for task in tasks:
            candidate_scores = self._rank_candidates(
                task,
                project,
                assigned_hours,
                assigned_tasks,
                task_embeddings[task["id"]],
            )
            best_candidate = candidate_scores[0]
            self._apply_assignment_load(
                best_candidate.member["id"],
                task["estimated_hours"],
                assigned_hours,
                assigned_tasks,
                ratio=1.0,
            )
            member_involvement[best_candidate.member["id"]] += 1
            task_assignments.append(
                {
                    "task_id": task["id"],
                    "task_title": task["title"],
                    "category": task["category"],
                    "priority": task["priority"],
                    "difficulty": task["difficulty"],
                    "estimated_hours": task["estimated_hours"],
                    "deadline_iso": task.get("deadline_iso", ""),
                    "required_skills": task["required_skills"],
                    "assigned_to": [
                        self._build_assignee_payload(
                            task,
                            best_candidate,
                            responsibility="primary",
                        )
                    ],
                    "top_alternatives": [
                        {
                            "member_id": option.member["id"],
                            "name": option.member["name"],
                            "role": option.member["role"],
                            "score": round(option.total_score, 4),
                        }
                        for option in candidate_scores[1:3]
                    ],
                }
            )

        task_assignments_by_id = {a["task_id"]: a for a in task_assignments}

        for member in self.team:
            if member_involvement[member["id"]] > 0:
                continue

            best_fit = self._choose_task_for_unassigned_member(
                member,
                project,
                tasks,
                task_embeddings,
                task_assignments_by_id,
                assigned_hours,
                assigned_tasks,
            )
            if best_fit is None:
                continue

            task, candidate = best_fit
            task_assignment = task_assignments_by_id[task["id"]]
            self._apply_assignment_load(
                member["id"],
                task["estimated_hours"],
                assigned_hours,
                assigned_tasks,
                ratio=self.COLLABORATOR_LOAD_RATIO,
            )
            member_involvement[member["id"]] += 1
            task_assignment["assigned_to"].append(
                self._build_assignee_payload(
                    task,
                    candidate,
                    responsibility="collaborator",
                    extra_reason="добавлен как соисполнитель, чтобы вовлечь участника в проект и усилить задачу близкими навыками",
                )
            )

        for task in tasks:
            task_assignment = task_assignments_by_id[task["id"]]
            self._maybe_add_strong_collaborator(
                task,
                project,
                task_assignment,
                task_embeddings[task["id"]],
                assigned_hours,
                assigned_tasks,
                member_involvement,
            )

        return {
            "project_id": project["id"],
            "project_title": project["title"],
            "team_coverage": {
                "assigned_members": sum(1 for c in member_involvement.values() if c > 0),
                "total_members": len(self.team),
            },
            "assignments": sorted(task_assignments, key=lambda item: item["task_id"]),
        }

    def _build_explanation(
        self,
        task: Dict[str, Any],
        candidate: CandidateScore,
        responsibility: str,
        extra_reason: str | None = None,
    ) -> str:
        reason_parts = []

        if candidate.overlap_skills:
            reason_parts.append(
                f"совпадают ключевые навыки: {', '.join(candidate.overlap_skills[:3])}"
            )
        else:
            reason_parts.append("профиль участника семантически близок описанию задачи")

        if candidate.role_score >= 1.0:
            reason_parts.append(
                f"роль `{candidate.member['role']}` хорошо подходит под категорию `{task['category']}`"
            )

        if candidate.remaining_capacity >= task["estimated_hours"]:
            reason_parts.append(
                f"у участника есть доступная емкость: осталось около {candidate.remaining_capacity} часов"
            )
        else:
            reason_parts.append(
                "кандидат выбран несмотря на ограниченную емкость, потому что лучше остальных совпал по навыкам"
            )

        if responsibility == "collaborator":
            reason_parts.append("назначен как второй исполнитель задачи")
        if extra_reason:
            reason_parts.append(extra_reason)

        reason_parts.append(
            f"итоговый score {candidate.total_score:.3f} при semantic={candidate.semantic_score:.3f}"
        )
        return "; ".join(reason_parts)
