from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from .embeddings import build_card_embedding_text, get_embedding_service
from .schema import (
    CARD_TYPES,
    DIFFICULTY_LEVELS,
    EXPERIENCE_LEVELS,
    FORMATS,
    LANGUAGES,
    ORGANIZERS,
    REGIONS,
    SKILLS,
    TOPICS,
    Paths,
    base_card_record,
)


@dataclass(slots=True)
class DatasetBundle:
    users: pd.DataFrame
    cards: pd.DataFrame
    interactions: pd.DataFrame


def load_settings(root: Path) -> dict[str, Any]:
    with (root / "config" / "settings.yaml").open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _pick(rng: np.random.Generator, items: list[str], low: int = 1, high: int = 3) -> list[str]:
    size = int(rng.integers(low, high + 1))
    return sorted(rng.choice(items, size=size, replace=False).tolist())


def _make_weight_map(
    rng: np.random.Generator,
    items: list[str],
    low: float,
    high: float,
) -> str:
    return json.dumps({item: round(float(rng.uniform(low, high)), 4) for item in items}, sort_keys=True)


def _build_title(card_type: str, topics: list[str], format_name: str, organizer: str) -> str:
    topic_a = topics[0].replace("_", " ").title()
    topic_b = topics[1].replace("_", " ").title() if len(topics) > 1 else "Innovation"
    if card_type == "hackathon":
        return f"{topic_a} x {topic_b} Hackathon"
    if card_type == "meetup":
        return f"{topic_a} Meetup for Student Builders"
    if card_type == "project":
        return f"{topic_a} Collaboration Project"
    if card_type == "course":
        return f"{topic_a} {format_name.title()} Course"
    return f"{organizer} Briefing on {topic_a}"


def _build_descriptions(
    card_type: str,
    title: str,
    topics: list[str],
    skills_required: list[str],
    skills_gained: list[str],
    organizer: str,
    format_name: str,
) -> tuple[str, str]:
    short = (
        f"{title}. Built for students interested in {', '.join(topics[:2])}. "
        f"Format: {format_name}. Organizer: {organizer}."
    )
    full = (
        f"{title} is a {card_type} opportunity focused on {', '.join(topics)}. "
        f"Students are expected to bring {', '.join(skills_required)} and can strengthen "
        f"{', '.join(skills_gained)} through a structured learning or collaboration experience."
    )
    return short, full

def generate_users(settings: dict[str, Any]) -> pd.DataFrame:
    rng = np.random.default_rng(settings["random_seed"])
    rows: list[dict[str, Any]] = []
    for idx in range(settings["data"]["users"]):
        interests = _pick(rng, TOPICS, low=2, high=4)
        skills = _pick(rng, SKILLS, low=2, high=5)
        rows.append(
            {
                "user_id": f"user_{idx:04d}",
                "interests": "|".join(interests),
                "skills": "|".join(skills),
                "interest_weights": _make_weight_map(rng, interests, low=0.75, high=1.45),
                "skill_weights": _make_weight_map(rng, skills, low=0.65, high=1.65),
                "experience_level": rng.choice(EXPERIENCE_LEVELS),
                "preferred_language": rng.choice(LANGUAGES, p=[0.6, 0.25, 0.15]),
                "region": rng.choice(REGIONS),
                "preferred_formats": "|".join(_pick(rng, FORMATS, low=1, high=2)),
                "onboarding_completed_at": (
                    datetime.utcnow() - timedelta(days=int(rng.integers(10, 120)))
                ).isoformat(),
            }
        )
    return pd.DataFrame(rows)


def generate_cards(settings: dict[str, Any]) -> pd.DataFrame:
    rng = np.random.default_rng(settings["random_seed"] + 1)
    embedding_service = get_embedding_service(settings)
    now = datetime.utcnow()
    rows: list[dict[str, Any]] = []
    per_pool = settings["data"]["cards_per_pool"]
    for card_type in CARD_TYPES:
        for idx in range(per_pool):
            topics = _pick(rng, TOPICS, low=1, high=3)
            skills_required = _pick(rng, SKILLS, low=1, high=3)
            skills_gained = _pick(rng, SKILLS, low=1, high=3)
            organizer = str(rng.choice(ORGANIZERS))
            format_name = str(rng.choice(FORMATS, p=[0.45, 0.25, 0.3]))
            title = _build_title(card_type, topics, format_name, organizer)
            short_description, full_description = _build_descriptions(
                card_type,
                title,
                topics,
                skills_required,
                skills_gained,
                organizer,
                format_name,
            )
            start_delta = int(rng.integers(-10, 60))
            duration_days = int(rng.integers(1, 60))
            start_date = now + timedelta(days=start_delta)
            end_date = start_date + timedelta(days=duration_days)
            deadline = start_date - timedelta(days=int(rng.integers(0, 14)))
            record = base_card_record()
            record.update(
                {
                    "card_id": f"{card_type}_{idx:04d}",
                    "card_type": card_type,
                    "title": title,
                    "short_description": short_description,
                    "full_description": full_description,
                    "topics": "|".join(topics),
                    "skills_required": "|".join(skills_required),
                    "skills_gained": "|".join(skills_gained),
                    "difficulty_level": rng.choice(DIFFICULTY_LEVELS, p=[0.35, 0.45, 0.2]),
                    "format": format_name,
                    "language": rng.choice(LANGUAGES, p=[0.6, 0.25, 0.15]),
                    "location": rng.choice(REGIONS),
                    "start_date": start_date.date().isoformat(),
                    "end_date": end_date.date().isoformat(),
                    "application_deadline": deadline.date().isoformat(),
                    "estimated_duration": duration_days,
                    "team_based": int(rng.random() > 0.45),
                    "host_organization": organizer,
                    "cost_type": rng.choice(["free", "paid", "scholarship"]),
                    "reward_type": rng.choice(["certificate", "cash", "network", "credit"]),
                    "eligibility_constraints": rng.choice(["none", "student", "region_limited"]),
                    "freshness_timestamp": (now - timedelta(days=int(rng.integers(0, 30)))).isoformat(),
                    "quality_score": round(float(rng.uniform(0.45, 0.99)), 4),
                    "popularity_score": round(float(rng.uniform(0.2, 0.98)), 4),
                    "editorial_priority": round(float(rng.uniform(0.0, 1.0)), 4),
                    "embedding_vector": "",
                    "status": rng.choice(["active", "active", "active", "hidden"]),
                    "integrity_score": round(float(rng.uniform(0.65, 1.0)), 4),
                }
            )
            if card_type == "hackathon":
                record.update(
                    {
                        "prize_pool": round(float(rng.uniform(100.0, 25000.0)), 2),
                        "team_size": int(rng.integers(1, 6)),
                        "submission_type": rng.choice(["prototype", "pitch", "research"]),
                        "domain_focus": rng.choice(topics),
                        "sponsor_tier": rng.choice(["local", "regional", "global"]),
                    }
                )
            elif card_type == "meetup":
                record.update(
                    {
                        "speaker_quality": round(float(rng.uniform(0.3, 1.0)), 4),
                        "agenda_density": round(float(rng.uniform(0.2, 1.0)), 4),
                        "seats_left": int(rng.integers(0, 500)),
                        "networking_relevance": round(float(rng.uniform(0.3, 1.0)), 4),
                    }
                )
            elif card_type == "project":
                record.update(
                    {
                        "role_requirements": "|".join(_pick(rng, SKILLS, low=1, high=3)),
                        "project_maturity": rng.choice(["idea", "mvp", "growth"]),
                        "expected_commitment": rng.choice(["low", "medium", "high"]),
                        "collaboration_mode": rng.choice(["async", "sync", "mixed"]),
                    }
                )
            elif card_type == "course":
                record.update(
                    {
                        "certification": int(rng.random() > 0.4),
                        "pace": rng.choice(["self-paced", "cohort", "bootcamp"]),
                        "duration_weeks": int(rng.integers(1, 16)),
                        "prerequisite_depth": rng.choice(["none", "basic", "advanced"]),
                    }
                )
            elif card_type == "news":
                record.update(
                    {
                        "recency_score": round(float(rng.uniform(0.4, 1.0)), 4),
                        "source_authority": round(float(rng.uniform(0.4, 1.0)), 4),
                        "topic_urgency": round(float(rng.uniform(0.2, 1.0)), 4),
                        "actionability_relevance": round(float(rng.uniform(0.2, 1.0)), 4),
                    }
                )
            rows.append(record)
    embedding_texts = [build_card_embedding_text(row) for row in rows]
    embedding_vectors = embedding_service.embed_texts(embedding_texts)
    for row, vector in zip(rows, embedding_vectors):
        row["embedding_vector"] = json.dumps(vector)
    return pd.DataFrame(rows)


def generate_interactions(
    users: pd.DataFrame,
    cards: pd.DataFrame,
    settings: dict[str, Any],
) -> pd.DataFrame:
    rng = np.random.default_rng(settings["random_seed"] + 2)
    card_lookup = cards.set_index("card_id")
    rows: list[dict[str, Any]] = []
    now = datetime.utcnow()
    history_size = settings["data"]["interaction_history_per_user"]
    for _, user in users.iterrows():
        user_interests = set(user["interests"].split("|"))
        user_skills = set(user["skills"].split("|"))
        candidate_ids = rng.choice(cards["card_id"], size=history_size, replace=False)
        for session_step, card_id in enumerate(candidate_ids, start=1):
            card = card_lookup.loc[card_id]
            card_topics = set(str(card["topics"]).split("|"))
            card_skills = set(str(card["skills_required"]).split("|"))
            topic_overlap = len(user_interests & card_topics)
            skill_overlap = len(user_skills & card_skills)
            quality = float(card["quality_score"])
            popularity = float(card["popularity_score"])
            relevance = 0.22 * topic_overlap + 0.18 * skill_overlap + 0.3 * quality + 0.2 * popularity
            relevance += 0.08 if user["preferred_language"] == card["language"] else -0.03
            relevance += 0.06 if user["region"] == card["location"] else 0.0
            relevance += 0.05 if card["format"] in user["preferred_formats"].split("|") else -0.02
            relevance += rng.normal(0.0, 0.08)
            open_prob = 1 / (1 + np.exp(-(relevance - 0.55)))
            like_prob = 1 / (1 + np.exp(-(relevance - 0.75)))
            share_prob = 1 / (1 + np.exp(-(relevance - 0.95)))
            long_view_prob = 1 / (1 + np.exp(-(relevance - 0.65)))
            skip_prob = 1 / (1 + np.exp(relevance - 0.55))
            disengage_prob = 1 / (1 + np.exp(relevance - 0.4))
            event_time = now - timedelta(
                days=int(rng.integers(0, 60)),
                hours=int(rng.integers(0, 24)),
                minutes=int(rng.integers(0, 60)),
            )
            rows.append(
                {
                    "user_id": user["user_id"],
                    "card_id": card_id,
                    "session_id": f"{user['user_id']}_session_{int(rng.integers(1, settings['data']['session_history_per_user'] + 1)):03d}",
                    "session_depth": session_step,
                    "shown_at": event_time.isoformat(),
                    "pool_type": card["card_type"],
                    "topic_overlap": topic_overlap,
                    "skill_overlap": skill_overlap,
                    "open": int(rng.random() < open_prob),
                    "like": int(rng.random() < like_prob),
                    "share": int(rng.random() < share_prob),
                    "long_view": int(rng.random() < long_view_prob),
                    "skip_fast": int(rng.random() < skip_prob),
                    "disengage": int(rng.random() < disengage_prob),
                    "dwell_time_seconds": max(1, int(rng.normal(25 + 30 * long_view_prob, 10))),
                }
            )
    frame = pd.DataFrame(rows).sort_values("shown_at").reset_index(drop=True)
    return frame


def build_datasets(root: Path) -> DatasetBundle:
    settings = load_settings(root)
    users = generate_users(settings)
    cards = generate_cards(settings)
    interactions = generate_interactions(users, cards, settings)
    return DatasetBundle(users=users, cards=cards, interactions=interactions)


def persist_datasets(root: Path, bundle: DatasetBundle) -> None:
    paths = Paths(root)
    bundle.users.to_csv(paths.users_raw, index=False)
    bundle.cards.to_csv(paths.cards_raw, index=False)
    bundle.interactions.to_csv(paths.interactions_raw, index=False)


def generate_and_save(root: Path) -> DatasetBundle:
    bundle = build_datasets(root)
    persist_datasets(root, bundle)
    return bundle
