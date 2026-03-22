"""TaskAssignmentModel: assign_project_data с hash-эмбеддингами (без GigaChat)."""

from __future__ import annotations

from app.modules.projects.task_assignment.hash_embeddings import HashEmbeddingProvider
from app.modules.projects.task_assignment.task_assigner import TaskAssignmentModel


def test_assign_project_data_uses_only_given_team():
    encoder = HashEmbeddingProvider(dim=64)
    model = TaskAssignmentModel(encoder=encoder)
    project = {
        "id": "p1",
        "title": "Demo",
        "description": "API",
        "domain": "dev",
        "tasks": [
            {
                "id": "t1",
                "title": "Write API",
                "description": "REST endpoints",
                "required_skills": ["python"],
                "category": "backend",
                "difficulty": "medium",
                "estimated_hours": 4,
                "priority": "must_have",
                "deadline_iso": "2026-06-01",
            }
        ],
    }
    team = [
        {
            "id": "u1",
            "name": "Alex",
            "role": "Backend Engineer",
            "skills": ["python"],
            "secondary_skills": [],
        }
    ]
    out = model.assign_project_data(project, team)
    assert out["project_id"] == "p1"
    assert len(out["assignments"]) == 1
    assert out["assignments"][0]["assigned_to"][0]["member_id"] == "u1"
