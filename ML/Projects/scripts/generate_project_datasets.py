from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from student_recsys.data_generation import generate_users, load_settings
from student_recsys.embeddings import get_embedding_service
from student_recsys.features import build_user_embedding
from student_recsys.schema import FORMATS, LANGUAGES, ORGANIZERS, REGIONS


PROJECT_BLUEPRINTS: list[dict[str, Any]] = [
    {
        "title": "AI Study Buddy MVP",
        "topics": ["ai", "data", "product"],
        "required_skills": ["python", "machine_learning", "prompt_engineering"],
        "skills_gained": ["analytics", "git", "sql"],
        "role_skills": ["python", "react", "design_thinking"],
        "project_maturity": "mvp",
        "expected_commitment": "medium",
        "collaboration_mode": "mixed",
        "difficulty_level": "intermediate",
        "team_based": 1,
        "duration_days": (28, 56),
    },
    {
        "title": "Climate Footprint Dashboard",
        "topics": ["climate", "data", "web"],
        "required_skills": ["python", "sql", "analytics"],
        "skills_gained": ["react", "design_thinking", "leadership"],
        "role_skills": ["analytics", "react", "public_speaking"],
        "project_maturity": "growth",
        "expected_commitment": "medium",
        "collaboration_mode": "async",
        "difficulty_level": "intermediate",
        "team_based": 1,
        "duration_days": (35, 70),
    },
    {
        "title": "Fintech Budget Coach",
        "topics": ["fintech", "mobile", "product"],
        "required_skills": ["javascript", "react", "analytics"],
        "skills_gained": ["sql", "leadership", "design_thinking"],
        "role_skills": ["react", "analytics", "figma"],
        "project_maturity": "idea",
        "expected_commitment": "low",
        "collaboration_mode": "sync",
        "difficulty_level": "beginner",
        "team_based": 1,
        "duration_days": (21, 42),
    },
    {
        "title": "Campus Robotics Explorer",
        "topics": ["robotics", "ai", "mobile"],
        "required_skills": ["python", "machine_learning", "git"],
        "skills_gained": ["leadership", "prompt_engineering", "public_speaking"],
        "role_skills": ["python", "machine_learning", "react"],
        "project_maturity": "mvp",
        "expected_commitment": "high",
        "collaboration_mode": "mixed",
        "difficulty_level": "advanced",
        "team_based": 1,
        "duration_days": (45, 84),
    },
    {
        "title": "Cybersecurity Simulation Lab",
        "topics": ["cybersecurity", "web", "product"],
        "required_skills": ["python", "javascript", "sql"],
        "skills_gained": ["analytics", "git", "leadership"],
        "role_skills": ["python", "javascript", "design_thinking"],
        "project_maturity": "growth",
        "expected_commitment": "high",
        "collaboration_mode": "async",
        "difficulty_level": "advanced",
        "team_based": 1,
        "duration_days": (42, 75),
    },
    {
        "title": "Inclusive Design System",
        "topics": ["design", "web", "product"],
        "required_skills": ["figma", "design_thinking", "javascript"],
        "skills_gained": ["react", "leadership", "public_speaking"],
        "role_skills": ["figma", "react", "design_thinking"],
        "project_maturity": "mvp",
        "expected_commitment": "medium",
        "collaboration_mode": "sync",
        "difficulty_level": "intermediate",
        "team_based": 1,
        "duration_days": (28, 49),
    },
    {
        "title": "Student Founder CRM",
        "topics": ["product", "web", "data"],
        "required_skills": ["sql", "javascript", "analytics"],
        "skills_gained": ["react", "leadership", "git"],
        "role_skills": ["analytics", "sql", "react"],
        "project_maturity": "growth",
        "expected_commitment": "medium",
        "collaboration_mode": "mixed",
        "difficulty_level": "intermediate",
        "team_based": 1,
        "duration_days": (35, 63),
    },
    {
        "title": "Prompt Engineering Mentor",
        "topics": ["ai", "product", "design"],
        "required_skills": ["prompt_engineering", "python", "design_thinking"],
        "skills_gained": ["analytics", "leadership", "public_speaking"],
        "role_skills": ["prompt_engineering", "python", "figma"],
        "project_maturity": "idea",
        "expected_commitment": "low",
        "collaboration_mode": "async",
        "difficulty_level": "beginner",
        "team_based": 0,
        "duration_days": (14, 35),
    },
    {
        "title": "Open Data Internship Matcher",
        "topics": ["data", "product", "web"],
        "required_skills": ["sql", "analytics", "python"],
        "skills_gained": ["javascript", "react", "leadership"],
        "role_skills": ["sql", "analytics", "javascript"],
        "project_maturity": "growth",
        "expected_commitment": "medium",
        "collaboration_mode": "mixed",
        "difficulty_level": "intermediate",
        "team_based": 1,
        "duration_days": (30, 60),
    },
    {
        "title": "Mobile Volunteer Coordination App",
        "topics": ["mobile", "product", "climate"],
        "required_skills": ["react", "javascript", "leadership"],
        "skills_gained": ["analytics", "public_speaking", "git"],
        "role_skills": ["react", "leadership", "figma"],
        "project_maturity": "mvp",
        "expected_commitment": "medium",
        "collaboration_mode": "sync",
        "difficulty_level": "beginner",
        "team_based": 1,
        "duration_days": (21, 45),
    },
    {
        "title": "Fraud Insight Studio",
        "topics": ["fintech", "data", "ai"],
        "required_skills": ["python", "machine_learning", "sql"],
        "skills_gained": ["analytics", "git", "leadership"],
        "role_skills": ["python", "machine_learning", "analytics"],
        "project_maturity": "growth",
        "expected_commitment": "high",
        "collaboration_mode": "async",
        "difficulty_level": "advanced",
        "team_based": 1,
        "duration_days": (42, 77),
    },
    {
        "title": "Youth Media Fact Checker",
        "topics": ["cybersecurity", "data", "design"],
        "required_skills": ["analytics", "python", "public_speaking"],
        "skills_gained": ["prompt_engineering", "leadership", "sql"],
        "role_skills": ["analytics", "design_thinking", "public_speaking"],
        "project_maturity": "idea",
        "expected_commitment": "low",
        "collaboration_mode": "mixed",
        "difficulty_level": "beginner",
        "team_based": 1,
        "duration_days": (18, 40),
    },
]


def _resolve_embedding_runtime(settings: dict[str, Any]) -> str:
    config = settings.get("embeddings", {})
    provider = str(config.get("provider", "gigachat")).lower()
    if provider != "gigachat":
        return provider
    env_name = str(config.get("auth_key_env", "GIGACHAT_AUTH_KEY"))
    auth_key = os.getenv(env_name, str(config.get("auth_key", ""))).strip()
    return "gigachat" if auth_key else "local_hash_fallback"


def _join(values: list[str]) -> str:
    return "|".join(values)


def _build_project_text(project: dict[str, Any]) -> str:
    lines = [
        f"title: {project['project_title']}",
        f"description: {project['project_summary']}",
        f"topics: {project['topics'].replace('|', ', ')}",
        f"required_skills: {project['required_skills'].replace('|', ', ')}",
        f"skills_gained: {project['skills_gained'].replace('|', ', ')}",
        f"role_skills: {project['role_skills'].replace('|', ', ')}",
        f"project_maturity: {project['project_maturity']}",
        f"expected_commitment: {project['expected_commitment']}",
        f"collaboration_mode: {project['collaboration_mode']}",
        f"format: {project['format']}",
        f"language: {project['language']}",
        f"location: {project['location']}",
    ]
    return "\n".join(lines)[:1500]


def _weighted_sum(weight_map: dict[str, float], tags: set[str]) -> float:
    return sum(float(weight_map.get(tag, 0.0)) for tag in tags)


def _commitment_fit(experience_level: str, expected_commitment: str) -> float:
    fit_map = {
        "newcomer": {"low": 1.0, "medium": 0.7, "high": 0.25},
        "junior": {"low": 0.9, "medium": 0.9, "high": 0.5},
        "mid": {"low": 0.6, "medium": 0.95, "high": 0.9},
        "senior": {"low": 0.5, "medium": 0.85, "high": 1.0},
    }
    return fit_map.get(experience_level, {}).get(expected_commitment, 0.5)


def _maturity_fit(experience_level: str, project_maturity: str) -> float:
    fit_map = {
        "newcomer": {"idea": 1.0, "mvp": 0.75, "growth": 0.45},
        "junior": {"idea": 0.9, "mvp": 0.9, "growth": 0.65},
        "mid": {"idea": 0.65, "mvp": 0.95, "growth": 0.95},
        "senior": {"idea": 0.6, "mvp": 0.9, "growth": 1.0},
    }
    return fit_map.get(experience_level, {}).get(project_maturity, 0.5)


def generate_project_catalog(settings: dict[str, Any]) -> pd.DataFrame:
    rng = np.random.default_rng(settings["random_seed"] + 101)
    embedding_service = get_embedding_service(settings)
    now = datetime.now(UTC)
    rows: list[dict[str, Any]] = []
    total_projects = int(settings["data"]["cards_per_pool"])

    for idx in range(total_projects):
        blueprint = PROJECT_BLUEPRINTS[idx % len(PROJECT_BLUEPRINTS)]
        organizer = str(rng.choice(ORGANIZERS))
        format_name = str(rng.choice(FORMATS, p=[0.5, 0.15, 0.35]))
        language = str(rng.choice(LANGUAGES, p=[0.5, 0.35, 0.15]))
        location = str(rng.choice(REGIONS))
        duration_days = int(rng.integers(*blueprint["duration_days"])) + 1
        project_start = now + timedelta(days=int(rng.integers(3, 40)))
        apply_deadline = project_start - timedelta(days=int(rng.integers(2, 12)))
        title = f"{blueprint['title']} - {organizer}"
        summary = (
            f"{title} for students interested in {', '.join(blueprint['topics'])}. "
            f"Needs {', '.join(blueprint['required_skills'])}; helps grow {', '.join(blueprint['skills_gained'])}."
        )
        rows.append(
            {
                "project_id": f"project_{idx:04d}",
                "project_title": title,
                "project_summary": summary,
                "topics": _join(blueprint["topics"]),
                "required_skills": _join(blueprint["required_skills"]),
                "skills_gained": _join(blueprint["skills_gained"]),
                "role_skills": _join(blueprint["role_skills"]),
                "project_maturity": blueprint["project_maturity"],
                "expected_commitment": blueprint["expected_commitment"],
                "collaboration_mode": blueprint["collaboration_mode"],
                "difficulty_level": blueprint["difficulty_level"],
                "team_based": int(blueprint["team_based"]),
                "format": format_name,
                "language": language,
                "location": location,
                "host_organization": organizer,
                "project_start_date": project_start.date().isoformat(),
                "application_deadline": apply_deadline.date().isoformat(),
                "estimated_duration_days": duration_days,
                "embedding_vector": "",
            }
        )

    embedding_vectors = embedding_service.embed_texts([_build_project_text(row) for row in rows])
    for row, vector in zip(rows, embedding_vectors):
        row["embedding_vector"] = json.dumps(vector)
    return pd.DataFrame(rows)


def generate_project_skill_map(project_catalog: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    importance = {"required": 1.0, "role": 0.85, "gained": 0.55}
    for _, project in project_catalog.iterrows():
        for skill in str(project["required_skills"]).split("|"):
            rows.append(
                {
                    "project_id": project["project_id"],
                    "skill_name": skill,
                    "skill_type": "required",
                    "importance_weight": importance["required"],
                }
            )
        for skill in str(project["role_skills"]).split("|"):
            rows.append(
                {
                    "project_id": project["project_id"],
                    "skill_name": skill,
                    "skill_type": "role",
                    "importance_weight": importance["role"],
                }
            )
        for skill in str(project["skills_gained"]).split("|"):
            rows.append(
                {
                    "project_id": project["project_id"],
                    "skill_name": skill,
                    "skill_type": "gained",
                    "importance_weight": importance["gained"],
                }
            )
    return pd.DataFrame(rows)


def generate_skill_catalog(project_skill_map: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        project_skill_map.groupby(["skill_name", "skill_type"])
        .agg(project_count=("project_id", "nunique"), avg_importance=("importance_weight", "mean"))
        .reset_index()
        .sort_values(["project_count", "skill_name"], ascending=[False, True])
    )
    return grouped


def generate_user_profiles(
    settings: dict[str, Any],
    project_catalog: pd.DataFrame,
) -> pd.DataFrame:
    raw_users = generate_users(settings)
    empty_interactions = pd.DataFrame(columns=["user_id", "card_id", "shown_at", "like", "share", "open", "long_view", "skip_fast", "disengage"])
    project_cards_for_embedding = project_catalog.rename(columns={"project_id": "card_id", "required_skills": "skills_required"})

    profiles = raw_users[
        [
            "user_id",
            "interests",
            "interest_weights",
            "skills",
            "skill_weights",
            "experience_level",
            "preferred_language",
            "region",
            "preferred_formats",
        ]
    ].copy()

    embeddings: list[str] = []
    for _, user in profiles.iterrows():
        vector = build_user_embedding(user, empty_interactions, project_cards_for_embedding).tolist()
        embeddings.append(json.dumps(vector))
    profiles["user_embedding"] = embeddings
    return profiles


def generate_user_project_reactions(
    user_profiles: pd.DataFrame,
    project_catalog: pd.DataFrame,
    settings: dict[str, Any],
) -> pd.DataFrame:
    rng = np.random.default_rng(settings["random_seed"] + 102)
    project_lookup = project_catalog.set_index("project_id")
    rows: list[dict[str, Any]] = []
    now = datetime.now(UTC)
    history_size = min(int(settings["data"]["interaction_history_per_user"]), len(project_catalog))

    for _, user in user_profiles.iterrows():
        interest_weights = json.loads(str(user["interest_weights"]))
        skill_weights = json.loads(str(user["skill_weights"]))
        user_topics = set(str(user["interests"]).split("|"))
        user_skills = set(str(user["skills"]).split("|"))
        candidate_ids = rng.choice(project_catalog["project_id"], size=history_size, replace=False)

        for step, project_id in enumerate(candidate_ids, start=1):
            project = project_lookup.loc[project_id]
            topics = set(str(project["topics"]).split("|"))
            required = set(str(project["required_skills"]).split("|"))
            gained = set(str(project["skills_gained"]).split("|"))
            role = set(str(project["role_skills"]).split("|"))

            topic_match = _weighted_sum(interest_weights, user_topics & topics)
            required_skill_match = _weighted_sum(skill_weights, user_skills & required)
            gained_skill_match = _weighted_sum(skill_weights, user_skills & gained)
            role_skill_match = _weighted_sum(skill_weights, user_skills & role)
            readiness_score = 0.7 * required_skill_match + 0.3 * gained_skill_match

            relevance = 0.24 * topic_match
            relevance += 0.36 * required_skill_match
            relevance += 0.12 * gained_skill_match
            relevance += 0.12 * role_skill_match
            relevance += 0.08 * _commitment_fit(str(user["experience_level"]), str(project["expected_commitment"]))
            relevance += 0.08 * _maturity_fit(str(user["experience_level"]), str(project["project_maturity"]))
            relevance += 0.05 if user["preferred_language"] == project["language"] else -0.03
            relevance += 0.05 if user["region"] == project["location"] else 0.0
            relevance += 0.05 if project["format"] in str(user["preferred_formats"]).split("|") else -0.02
            relevance += 0.05 * readiness_score
            relevance += rng.normal(0.0, 0.1)

            open_prob = 1 / (1 + np.exp(-(relevance - 0.75)))
            like_prob = 1 / (1 + np.exp(-(relevance - 0.95)))
            share_prob = 1 / (1 + np.exp(-(relevance - 1.1)))
            long_view_prob = 1 / (1 + np.exp(-(relevance - 0.85)))
            skip_fast_prob = 1 / (1 + np.exp(relevance - 0.8))
            disengage_prob = 1 / (1 + np.exp(relevance - 0.65))

            shown_at = now - timedelta(
                days=int(rng.integers(0, 45)),
                hours=int(rng.integers(0, 24)),
                minutes=int(rng.integers(0, 60)),
            )
            rows.append(
                {
                    "user_id": user["user_id"],
                    "project_id": project_id,
                    "shown_at": shown_at.isoformat(),
                    "session_depth": step,
                    "topic_match_score": round(topic_match, 4),
                    "required_skill_match_score": round(required_skill_match, 4),
                    "gained_skill_match_score": round(gained_skill_match, 4),
                    "role_skill_match_score": round(role_skill_match, 4),
                    "readiness_score": round(readiness_score, 4),
                    "open": int(rng.random() < open_prob),
                    "like": int(rng.random() < like_prob),
                    "share": int(rng.random() < share_prob),
                    "long_view": int(rng.random() < long_view_prob),
                    "skip_fast": int(rng.random() < skip_fast_prob),
                    "disengage": int(rng.random() < disengage_prob),
                }
            )

    return pd.DataFrame(rows).sort_values("shown_at").reset_index(drop=True)


def build_recommendation_pairs(
    user_profiles: pd.DataFrame,
    project_catalog: pd.DataFrame,
    user_project_reactions: pd.DataFrame,
) -> pd.DataFrame:
    reaction_lookup = user_project_reactions.set_index(["user_id", "project_id"])
    project_lookup = project_catalog.set_index("project_id")
    rows: list[dict[str, Any]] = []

    for _, user in user_profiles.iterrows():
        interest_weights = json.loads(str(user["interest_weights"]))
        skill_weights = json.loads(str(user["skill_weights"]))
        user_topics = set(str(user["interests"]).split("|"))
        user_skills = set(str(user["skills"]).split("|"))
        user_vector = np.array(json.loads(str(user["user_embedding"])), dtype=float)

        for project_id, project in project_lookup.iterrows():
            topics = set(str(project["topics"]).split("|"))
            required = set(str(project["required_skills"]).split("|"))
            gained = set(str(project["skills_gained"]).split("|"))
            role = set(str(project["role_skills"]).split("|"))
            topic_match = _weighted_sum(interest_weights, user_topics & topics)
            required_skill_match = _weighted_sum(skill_weights, user_skills & required)
            gained_skill_match = _weighted_sum(skill_weights, user_skills & gained)
            role_skill_match = _weighted_sum(skill_weights, user_skills & role)
            readiness_score = 0.7 * required_skill_match + 0.3 * gained_skill_match
            project_vector = np.array(json.loads(str(project["embedding_vector"])), dtype=float)
            embedding_similarity = 0.0
            if user_vector.size and project_vector.size:
                denom = float(np.linalg.norm(user_vector) * np.linalg.norm(project_vector)) or 1.0
                embedding_similarity = float(np.dot(user_vector, project_vector) / denom)

            row = {
                "user_id": user["user_id"],
                "project_id": project_id,
                "topic_match_score": round(topic_match, 4),
                "required_skill_match_score": round(required_skill_match, 4),
                "gained_skill_match_score": round(gained_skill_match, 4),
                "role_skill_match_score": round(role_skill_match, 4),
                "readiness_score": round(readiness_score, 4),
                "embedding_similarity": round(embedding_similarity, 6),
                "commitment_fit": round(
                    _commitment_fit(str(user["experience_level"]), str(project["expected_commitment"])),
                    4,
                ),
                "maturity_fit": round(
                    _maturity_fit(str(user["experience_level"]), str(project["project_maturity"])),
                    4,
                ),
            }
            if (user["user_id"], project_id) in reaction_lookup.index:
                reaction = reaction_lookup.loc[(user["user_id"], project_id)]
                for target in ["open", "like", "share", "long_view", "skip_fast", "disengage"]:
                    row[target] = int(reaction[target])
            else:
                for target in ["open", "like", "share", "long_view", "skip_fast", "disengage"]:
                    row[target] = 0
            rows.append(row)

    return pd.DataFrame(rows)


def _clear_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        for path in output_dir.iterdir():
            if path.is_file():
                path.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)


def generate_project_datasets(root: Path) -> dict[str, Any]:
    settings = load_settings(root)
    output_dir = root / "data" / "projects"
    _clear_output_dir(output_dir)

    project_catalog = generate_project_catalog(settings)
    project_skill_map = generate_project_skill_map(project_catalog)
    skill_catalog = generate_skill_catalog(project_skill_map)
    user_profiles = generate_user_profiles(settings, project_catalog)
    user_project_reactions = generate_user_project_reactions(user_profiles, project_catalog, settings)
    recommendation_pairs = build_recommendation_pairs(user_profiles, project_catalog, user_project_reactions)

    project_catalog.to_csv(output_dir / "project_catalog.csv", index=False)
    project_skill_map.to_csv(output_dir / "project_skill_map.csv", index=False)
    skill_catalog.to_csv(output_dir / "skill_catalog.csv", index=False)
    user_profiles.to_csv(output_dir / "user_profiles.csv", index=False)
    user_project_reactions.to_csv(output_dir / "user_project_reactions.csv", index=False)
    recommendation_pairs.to_csv(output_dir / "project_recommendation_pairs.csv", index=False)

    metadata = {
        "generated_at": datetime.now(UTC).isoformat(),
        "embedding_runtime": _resolve_embedding_runtime(settings),
        "projects": len(project_catalog),
        "project_skill_links": len(project_skill_map),
        "skills": int(skill_catalog["skill_name"].nunique()),
        "users": len(user_profiles),
        "reactions": len(user_project_reactions),
        "recommendation_pairs": len(recommendation_pairs),
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


if __name__ == "__main__":
    print(json.dumps(generate_project_datasets(ROOT), indent=2))
