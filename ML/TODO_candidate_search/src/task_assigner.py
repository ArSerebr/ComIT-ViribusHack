import json
from dataclasses import dataclass
from math import ceil
from pathlib import Path
from typing import Dict, List

from src.gigachat_embeddings import GigaChatEmbeddingsClient


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def cosine_similarity(left: List[float], right: List[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right))


def textify_member(member: Dict) -> str:
    return " ".join(
        [
            member["name"],
            member["role"],
            member["bio"],
            " ".join(member["skills"]),
            " ".join(member["secondary_skills"]),
        ]
    )


def textify_task(project: Dict, task: Dict) -> str:
    return " ".join(
        [
            project["title"],
            project["description"],
            task["title"],
            task["description"],
            " ".join(task["required_skills"]),
            task["category"],
            task["difficulty"],
        ]
    )


ROLE_HINTS = {
    "product": ["Product Manager", "Business Analyst", "Project Coordinator"],
    "design": ["UX/UI Designer", "Product Designer"],
    "frontend": ["Frontend Engineer", "Fullstack Engineer"],
    "backend": ["Backend Engineer", "Backend / Security", "Fullstack Engineer"],
    "mobile": ["Mobile Engineer"],
    "devops": ["DevOps Engineer"],
    "qa": ["QA Engineer", "QA Automation Engineer"],
    "analytics": ["Data Analyst", "Growth Analyst", "Product Manager"],
    "ml": ["Data Scientist"],
}


@dataclass
class CandidateScore:
    member: Dict
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

    def __init__(self, projects_path: Path, team_path: Path):
        self.projects = load_json(projects_path)
        self.team = load_json(team_path)
        self.encoder = GigaChatEmbeddingsClient()
        member_texts = [textify_member(member) for member in self.team]
        member_vectors = self.encoder.embed_texts(member_texts)
        self.member_embeddings = {
            member["id"]: member_vectors[index] for index, member in enumerate(self.team)
        }
        self.project_index = {project["id"]: project for project in self.projects}

    def _rank_candidates(
        self,
        task: Dict,
        project: Dict,
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
        task: Dict,
        project: Dict,
        member: Dict,
        assigned_hours: Dict[str, int],
        assigned_tasks: Dict[str, int],
        task_embedding: List[float],
    ) -> CandidateScore:
        member_embedding = self.member_embeddings[member["id"]]
        semantic_score = cosine_similarity(task_embedding, member_embedding)

        member_skill_pool = {skill.lower() for skill in member["skills"] + member["secondary_skills"]}
        required_skills = [skill.lower() for skill in task["required_skills"]]
        overlap_skills = [skill for skill in task["required_skills"] if skill.lower() in member_skill_pool]
        skills_score = len(overlap_skills) / max(1, len(required_skills))

        preferred_roles = ROLE_HINTS.get(task["category"], [])
        role_score = 1.0 if member["role"] in preferred_roles else 0.2

        max_capacity = member["availability_hours_per_week"] * 4
        remaining_capacity = max_capacity - member["current_load_hours"] - assigned_hours[member["id"]]
        workload_ratio = max(0.0, min(1.0, remaining_capacity / max(1, max_capacity)))
        task_slots_left = member["max_parallel_tasks"] - assigned_tasks[member["id"]]
        parallel_ratio = max(0.0, min(1.0, task_slots_left / max(1, member["max_parallel_tasks"])))
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
        task: Dict,
        candidate: CandidateScore,
        responsibility: str,
        extra_reason: str | None = None,
    ) -> Dict:
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
        member: Dict,
        project: Dict,
        tasks: List[Dict],
        task_embeddings: Dict[str, List[float]],
        task_assignments_by_id: Dict[str, Dict],
        assigned_hours: Dict[str, int],
        assigned_tasks: Dict[str, int],
    ) -> tuple[Dict, CandidateScore] | None:
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
        task: Dict,
        project: Dict,
        task_assignment: Dict,
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

    def assign_project(self, project_id: str) -> Dict:
        project = self.project_index.get(project_id)
        if not project:
            raise ValueError(f"Project with id '{project_id}' not found")

        assigned_hours = {member["id"]: 0 for member in self.team}
        assigned_tasks = {member["id"]: 0 for member in self.team}
        member_involvement = {member["id"]: 0 for member in self.team}
        task_assignments = []
        task_texts = [textify_task(project, task) for task in project["tasks"]]
        task_vectors = self.encoder.embed_texts(task_texts)
        task_embeddings = {
            task["id"]: task_vectors[index] for index, task in enumerate(project["tasks"])
        }

        tasks = sorted(
            project["tasks"],
            key=lambda task: (
                {"must_have": 0, "should_have": 1, "nice_to_have": 2}[task["priority"]],
                {"high": 0, "medium": 1, "low": 2}[task["difficulty"]],
                -task["estimated_hours"],
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

        task_assignments_by_id = {
            assignment["task_id"]: assignment for assignment in task_assignments
        }

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
            "project_domain": project["domain"],
            "team_coverage": {
                "assigned_members": sum(1 for count in member_involvement.values() if count > 0),
                "total_members": len(self.team),
            },
            "assignments": sorted(task_assignments, key=lambda item: item["task_id"]),
        }

    def _build_explanation(
        self,
        task: Dict,
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
            reason_parts.append(f"роль `{candidate.member['role']}` хорошо подходит под категорию `{task['category']}`")

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
