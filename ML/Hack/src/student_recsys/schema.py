from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

CARD_TYPES = ["hackathon", "meetup", "project", "course", "news"]
FORMATS = ["online", "offline", "hybrid"]
LANGUAGES = ["en", "ru", "es"]
REGIONS = ["EU", "US", "MENA", "APAC", "LATAM"]
DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]
EXPERIENCE_LEVELS = ["newcomer", "junior", "mid", "senior"]
TOPICS = [
    "ai",
    "web",
    "mobile",
    "robotics",
    "design",
    "fintech",
    "product",
    "data",
    "cybersecurity",
    "climate",
]
SKILLS = [
    "python",
    "sql",
    "javascript",
    "machine_learning",
    "public_speaking",
    "design_thinking",
    "figma",
    "react",
    "analytics",
    "leadership",
    "git",
    "prompt_engineering",
]
ORGANIZERS = [
    "UniTech",
    "Campus Labs",
    "Future Founders",
    "Open Learning",
    "Global AI Club",
    "Career Forge",
    "HackSphere",
    "NextGen Labs",
]


@dataclass(slots=True)
class Paths:
    root: Path

    @property
    def config(self) -> Path:
        return self.root / "config" / "settings.yaml"

    @property
    def users_raw(self) -> Path:
        return self.root / "data" / "raw" / "users.csv"

    @property
    def cards_raw(self) -> Path:
        return self.root / "data" / "raw" / "cards.csv"

    @property
    def interactions_raw(self) -> Path:
        return self.root / "data" / "raw" / "interactions.csv"

    @property
    def ranked_training(self) -> Path:
        return self.root / "data" / "processed" / "ranker_training.csv"

    @property
    def retrieval_model(self) -> Path:
        return self.root / "models" / "retrieval.joblib"

    @property
    def ranker_model(self) -> Path:
        return self.root / "models" / "ranker.joblib"

    @property
    def metadata_model(self) -> Path:
        return self.root / "models" / "metadata.joblib"


def base_card_record() -> dict[str, Any]:
    return {
        "short_description": "",
        "full_description": "",
        "topics": "",
        "skills_required": "",
        "skills_gained": "",
        "difficulty_level": "",
        "format": "",
        "language": "",
        "location": "",
        "start_date": "",
        "end_date": "",
        "application_deadline": "",
        "estimated_duration": 0,
        "team_based": 0,
        "host_organization": "",
        "cost_type": "",
        "reward_type": "",
        "eligibility_constraints": "",
        "freshness_timestamp": "",
        "quality_score": 0.0,
        "popularity_score": 0.0,
        "editorial_priority": 0.0,
        "embedding_vector": "",
        "prize_pool": 0.0,
        "team_size": 0,
        "submission_type": "",
        "domain_focus": "",
        "sponsor_tier": "",
        "speaker_quality": 0.0,
        "agenda_density": 0.0,
        "seats_left": 0,
        "networking_relevance": 0.0,
        "role_requirements": "",
        "project_maturity": "",
        "expected_commitment": "",
        "collaboration_mode": "",
        "certification": 0,
        "pace": "",
        "duration_weeks": 0,
        "prerequisite_depth": "",
        "recency_score": 0.0,
        "source_authority": 0.0,
        "topic_urgency": 0.0,
        "actionability_relevance": 0.0,
        "status": "active",
        "integrity_score": 1.0,
    }
