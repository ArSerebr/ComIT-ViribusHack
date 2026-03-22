from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter, deque
from datetime import datetime, timedelta
from pathlib import Path

from gigachat_embedding_provider import embed_weighted_tokens


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

SEED = 42
NOW = datetime(2026, 3, 22, 12, 0, 0)
EMBED_DIM = 12
N_USERS = 320
N_NEWS = 240
SESSIONS_PER_USER = 6
SESSION_DEPTH_RANGE = (6, 10)
MIN_WEIGHT = 0.2
MAX_WEIGHT = 2.2

TOPICS = [
    "ai",
    "climate",
    "cybersecurity",
    "data",
    "design",
    "fintech",
    "mobile",
    "policy",
    "product",
    "research",
    "robotics",
    "science",
    "startups",
    "web",
]

SKILLS = [
    "analytics",
    "critical_thinking",
    "data_literacy",
    "design_thinking",
    "figma",
    "git",
    "javascript",
    "leadership",
    "machine_learning",
    "prompt_engineering",
    "public_speaking",
    "python",
    "react",
    "sql",
]

EXPERIENCE_LEVELS = ["newcomer", "junior", "mid", "senior"]
LANGUAGES = ["en", "ru", "es"]
REGIONS = ["US", "EU", "LATAM", "MENA", "APAC"]
FORMATS = ["briefing", "analysis", "live_blog", "explainer", "newsletter"]
NEWS_CATEGORIES = [
    "breaking",
    "research_digest",
    "policy_watch",
    "market_map",
    "product_launch",
    "student_opportunity",
]

SOURCE_PROFILES = {
    "TechWire": {"source_type": "newsroom", "authority": 0.93},
    "Campus Pulse": {"source_type": "student_media", "authority": 0.76},
    "Lab Chronicle": {"source_type": "research_lab", "authority": 0.97},
    "Policy Radar": {"source_type": "government_watch", "authority": 0.95},
    "Startup Signal": {"source_type": "industry_media", "authority": 0.88},
    "Builder Weekly": {"source_type": "company_blog", "authority": 0.82},
    "Global Science Desk": {"source_type": "science_media", "authority": 0.96},
    "Security Brief": {"source_type": "specialist_media", "authority": 0.94},
}

TOPIC_TO_SKILLS = {
    "ai": ["python", "machine_learning", "prompt_engineering", "analytics"],
    "climate": ["analytics", "critical_thinking", "public_speaking"],
    "cybersecurity": ["python", "sql", "critical_thinking"],
    "data": ["analytics", "sql", "python", "data_literacy"],
    "design": ["figma", "design_thinking", "public_speaking"],
    "fintech": ["analytics", "sql", "python", "product"],
    "mobile": ["react", "javascript", "product"],
    "policy": ["critical_thinking", "public_speaking", "data_literacy"],
    "product": ["product", "analytics", "leadership"],
    "research": ["critical_thinking", "python", "data_literacy"],
    "robotics": ["python", "machine_learning", "javascript"],
    "science": ["critical_thinking", "data_literacy", "python"],
    "startups": ["leadership", "product", "public_speaking"],
    "web": ["javascript", "react", "design_thinking"],
}

# Replace abstract placeholders with actual dataset skills.
TOPIC_TO_SKILLS["fintech"] = ["analytics", "sql", "python", "leadership"]
TOPIC_TO_SKILLS["mobile"] = ["react", "javascript", "design_thinking"]
TOPIC_TO_SKILLS["product"] = ["leadership", "analytics", "design_thinking"]
TOPIC_TO_SKILLS["startups"] = ["leadership", "product", "public_speaking"]

CATEGORY_TEMPLATES = {
    "breaking": [
        "{topic_title} alert reshapes student roadmap",
        "What changed in {topic_title} in the last 24 hours",
        "{topic_title} update every student should see today",
    ],
    "research_digest": [
        "New {topic_title} paper distilled for students",
        "{topic_title} research digest with practical takeaways",
        "What the latest {topic_title} study means right now",
    ],
    "policy_watch": [
        "{topic_title} policy shift students should track",
        "Fresh {topic_title} regulation update explained",
        "How the new {topic_title} rule changes the field",
    ],
    "market_map": [
        "{topic_title} market pulse and hiring signal",
        "Where {topic_title} momentum is moving this week",
        "{topic_title} demand snapshot for students and builders",
    ],
    "product_launch": [
        "New {topic_title} launch worth your attention",
        "{topic_title} product release with immediate implications",
        "What the latest {topic_title} launch unlocks",
    ],
    "student_opportunity": [
        "{topic_title} opportunity roundup for active students",
        "Fresh {topic_title} news with direct student upside",
        "{topic_title} moves that create student openings",
    ],
}

URGENT_TOPICS = {"ai", "cybersecurity", "policy", "climate", "startups"}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def entropy(values: list[str]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    total = sum(counts.values())
    result = 0.0
    for count in counts.values():
        probability = count / total
        result -= probability * math.log(probability + 1e-12)
    return result


def iso(dt: datetime) -> str:
    return dt.isoformat()


def serialize_pipe(values: list[str]) -> str:
    return "|".join(values)


def serialize_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=True, separators=(",", ":"))


def normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return [0.0] * len(vector)
    return [round(value / norm, 4) for value in vector]


def build_embedding(weighted_tokens: list[tuple[str, float]]) -> list[float]:
    return embed_weighted_tokens(weighted_tokens)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return clamp(numerator / (norm_a * norm_b), -1.0, 1.0)


def sample_unique(rng: random.Random, values: list[str], low: int, high: int) -> list[str]:
    size = rng.randint(low, high)
    return sorted(rng.sample(values, size))


def topic_title(topic: str) -> str:
    return topic.replace("_", " ").title()


def freshness_score(hours_since_update: float) -> float:
    return clamp(math.exp(-hours_since_update / 30.0), 0.0, 1.0)


def weighted_topic_overlap(topics: list[str], weights: dict[str, float]) -> tuple[float, float, int]:
    matched = [weights[topic] for topic in topics if topic in weights]
    if not matched:
        return 0.0, 0.0, 0
    return clamp(mean(matched) / 1.7, 0.0, 1.0), mean(matched), len(matched)


def weighted_skill_overlap(skills: list[str], weights: dict[str, float]) -> tuple[float, float, int]:
    matched = [weights[skill] for skill in skills if skill in weights]
    if not matched:
        return 0.0, 0.0, 0
    return clamp(mean(matched) / 1.7, 0.0, 1.0), mean(matched), len(matched)


def source_weight(source_loyalty_weights: dict[str, float], source_name: str) -> float:
    return source_loyalty_weights.get(source_name, 0.95)


def format_match(user_formats: list[str], news_format: str) -> float:
    return 1.0 if news_format in user_formats else 0.0


def language_match(user_language: str, news_language: str) -> float:
    return 1.0 if user_language == news_language else 0.0


def region_match(user_region: str, news_region: str) -> float:
    return 1.0 if news_region in {user_region, "Global"} else 0.0


def recency_bucket(hours_ago: float) -> str:
    if hours_ago <= 6:
        return "last_6h"
    if hours_ago <= 24:
        return "last_24h"
    if hours_ago <= 72:
        return "last_72h"
    return "older"


def choose_weighted(rng: random.Random, scored_items: list[tuple[float, dict]]) -> dict:
    max_score = max(score for score, _ in scored_items)
    weights = [math.exp(score - max_score) for score, _ in scored_items]
    choice = rng.choices(scored_items, weights=weights, k=1)[0]
    return choice[1]


def current_user_embedding(
    interest_weights: dict[str, float],
    skill_weights: dict[str, float],
    recent_positive_embeddings: list[list[float]],
) -> list[float]:
    weighted_tokens: list[tuple[str, float]] = []
    for topic, weight in interest_weights.items():
        weighted_tokens.append((f"topic::{topic}", weight))
    for skill, weight in skill_weights.items():
        weighted_tokens.append((f"skill::{skill}", weight * 1.25))
    base = build_embedding(weighted_tokens)
    if not recent_positive_embeddings:
        return base
    positive_mean = [
        mean([embedding[idx] for embedding in recent_positive_embeddings])
        for idx in range(EMBED_DIM)
    ]
    blended = [base[idx] * 0.72 + positive_mean[idx] * 0.28 for idx in range(EMBED_DIM)]
    return normalize_vector(blended)


def generate_users(rng: random.Random) -> tuple[list[dict], dict[str, dict]]:
    users: list[dict] = []
    internal_users: dict[str, dict] = {}
    for idx in range(N_USERS):
        user_id = f"user_{idx:04d}"
        interests = sample_unique(rng, TOPICS, 3, 6)
        skills = sample_unique(rng, SKILLS, 2, 5)

        interest_weights = {
            interest: round(rng.uniform(0.65, 1.7), 4) for interest in interests
        }
        skill_weights = {skill: round(rng.uniform(0.6, 1.8), 4) for skill in skills}

        preferred_language = rng.choices(LANGUAGES, weights=[0.6, 0.22, 0.18], k=1)[0]
        region = rng.choice(REGIONS)
        preferred_formats = sample_unique(rng, FORMATS, 2, 3)
        favorite_sources = sample_unique(rng, list(SOURCE_PROFILES.keys()), 2, 4)
        source_loyalty_weights = {
            source: round(rng.uniform(0.95, 1.45), 4) for source in favorite_sources
        }

        freshness_preference = round(rng.uniform(0.8, 1.55), 4)
        breaking_affinity = round(rng.uniform(0.75, 1.6), 4)

        user_row = {
            "user_id": user_id,
            "interests": serialize_pipe(interests),
            "skills": serialize_pipe(skills),
            "interest_weights": serialize_json(interest_weights),
            "skill_weights": serialize_json(skill_weights),
            "experience_level": rng.choice(EXPERIENCE_LEVELS),
            "preferred_language": preferred_language,
            "region": region,
            "preferred_formats": serialize_pipe(preferred_formats),
            "freshness_preference": freshness_preference,
            "breaking_affinity": breaking_affinity,
            "source_loyalty_weights": serialize_json(source_loyalty_weights),
            "onboarding_completed_at": iso(
                NOW - timedelta(days=rng.randint(7, 120), hours=rng.randint(0, 23))
            ),
        }
        users.append(user_row)
        internal_users[user_id] = {
            "interests": interests,
            "skills": skills,
            "interest_weights": interest_weights,
            "skill_weights": skill_weights,
            "preferred_language": preferred_language,
            "region": region,
            "preferred_formats": preferred_formats,
            "freshness_preference": freshness_preference,
            "breaking_affinity": breaking_affinity,
            "source_loyalty_weights": source_loyalty_weights,
        }
    return users, internal_users


def build_title(rng: random.Random, topics: list[str], category: str) -> str:
    template = rng.choice(CATEGORY_TEMPLATES[category])
    return template.format(topic_title=topic_title(topics[0]))


def build_news_cards(rng: random.Random) -> tuple[list[dict], dict[str, dict]]:
    cards: list[dict] = []
    internal_cards: dict[str, dict] = {}
    for idx in range(N_NEWS):
        card_id = f"news_{idx:04d}"
        category = rng.choices(
            NEWS_CATEGORIES,
            weights=[0.22, 0.16, 0.15, 0.17, 0.14, 0.16],
            k=1,
        )[0]
        topics = sample_unique(rng, TOPICS, 1, 3)
        related_skill_pool = []
        for topic in topics:
            related_skill_pool.extend(TOPIC_TO_SKILLS.get(topic, []))
        related_skill_pool = sorted(set(skill for skill in related_skill_pool if skill in SKILLS))
        skills_required = sample_unique(rng, related_skill_pool or SKILLS, 1, min(3, len(related_skill_pool or SKILLS)))
        remaining_skills = [skill for skill in SKILLS if skill not in skills_required]
        skills_gained = sample_unique(
            rng,
            remaining_skills,
            1,
            2,
        )

        source_name = rng.choice(list(SOURCE_PROFILES.keys()))
        source_type = SOURCE_PROFILES[source_name]["source_type"]
        source_authority = SOURCE_PROFILES[source_name]["authority"]
        news_format = rng.choices(FORMATS, weights=[0.24, 0.26, 0.12, 0.18, 0.2], k=1)[0]
        news_language = rng.choices(LANGUAGES, weights=[0.62, 0.22, 0.16], k=1)[0]
        location = rng.choices(REGIONS + ["Global"], weights=[1, 1, 1, 1, 1, 2.2], k=1)[0]

        hours_ago = min(rng.expovariate(1 / 26.0), 132.0)
        published_at = NOW - timedelta(hours=hours_ago + rng.uniform(0.3, 9.0))
        updated_at = NOW - timedelta(hours=max(hours_ago - rng.uniform(0.0, 4.0), 0.0))
        recency_score = freshness_score(hours_ago)
        breaking_score = clamp(
            (1.0 if category == "breaking" else 0.45 if category == "policy_watch" else 0.2)
            * (0.55 + recency_score),
            0.0,
            1.0,
        )
        topic_urgency = clamp(
            mean([1.0 if topic in URGENT_TOPICS else 0.62 for topic in topics])
            * (0.55 + 0.45 * recency_score),
            0.0,
            1.0,
        )
        actionability_relevance = clamp(
            (0.82 if category in {"policy_watch", "student_opportunity", "product_launch"} else 0.58)
            + rng.uniform(-0.12, 0.15),
            0.0,
            1.0,
        )
        novelty_score = clamp(0.45 + rng.uniform(-0.1, 0.45) + recency_score * 0.18, 0.0, 1.0)
        quality_score = clamp(source_authority * 0.55 + rng.uniform(0.2, 0.42), 0.0, 1.0)
        popularity_score = clamp(
            0.22 + recency_score * 0.48 + rng.uniform(0.0, 0.35) + (0.08 if "ai" in topics else 0.0),
            0.0,
            1.0,
        )
        editorial_priority = clamp(
            0.18 + topic_urgency * 0.32 + actionability_relevance * 0.25 + rng.uniform(0.0, 0.28),
            0.0,
            1.0,
        )
        integrity_score = clamp(source_authority * 0.7 + rng.uniform(0.15, 0.28), 0.0, 1.0)
        estimated_read_time_minutes = rng.randint(2, 14)
        status = "active" if recency_score >= 0.18 and integrity_score >= 0.72 else "hidden"

        title = build_title(rng, topics, category)
        short_description = (
            f"{source_name} covers {', '.join(topics)} for students who want personally relevant, current news."
        )
        full_description = (
            f"{title} focuses on {', '.join(topics)} and explains why the update matters now. "
            f"It is written for students who bring {', '.join(skills_required)} and can deepen "
            f"{', '.join(skills_gained)} while staying current on fast-moving developments."
        )

        embedding = build_embedding(
            [(f"topic::{topic}", 1.2) for topic in topics]
            + [(f"skill::{skill}", 1.35) for skill in skills_required]
            + [(f"skill::{skill}", 0.85) for skill in skills_gained]
            + [(f"source::{source_name}", 0.6), (f"category::{category}", 0.8)]
        )

        row = {
            "card_id": card_id,
            "card_type": "news",
            "title": title,
            "short_description": short_description,
            "full_description": full_description,
            "topics": serialize_pipe(topics),
            "skills_required": serialize_pipe(skills_required),
            "skills_gained": serialize_pipe(skills_gained),
            "news_category": category,
            "format": news_format,
            "language": news_language,
            "location": location,
            "published_at": iso(published_at),
            "updated_at": iso(updated_at),
            "freshness_timestamp": iso(updated_at),
            "source_name": source_name,
            "source_type": source_type,
            "author_name": f"{topic_title(topics[0])} Desk",
            "estimated_read_time_minutes": estimated_read_time_minutes,
            "quality_score": round(quality_score, 4),
            "popularity_score": round(popularity_score, 4),
            "editorial_priority": round(editorial_priority, 4),
            "source_authority": round(source_authority, 4),
            "topic_urgency": round(topic_urgency, 4),
            "actionability_relevance": round(actionability_relevance, 4),
            "recency_score": round(recency_score, 4),
            "breaking_score": round(breaking_score, 4),
            "novelty_score": round(novelty_score, 4),
            "integrity_score": round(integrity_score, 4),
            "status": status,
            "embedding_vector": serialize_json(embedding),
        }
        cards.append(row)
        internal_cards[card_id] = {
            **row,
            "topics_list": topics,
            "skills_required_list": skills_required,
            "skills_gained_list": skills_gained,
            "embedding": embedding,
            "hours_ago": hours_ago,
        }
    cards.sort(key=lambda item: item["card_id"])
    return cards, internal_cards


def compute_live_features(
    user_state: dict,
    card: dict,
    recent_history: list[dict],
    user_embedding: list[float],
    session_depth: int,
) -> dict:
    retrieval_similarity = clamp(
        (cosine_similarity(user_embedding, card["embedding"]) + 1.0) / 2.0,
        0.0,
        1.0,
    )
    topic_overlap_score, interest_weight_mean, interest_match_count = weighted_topic_overlap(
        card["topics_list"], user_state["interest_weights"]
    )
    skill_overlap_score, skill_weight_mean, skill_match_count = weighted_skill_overlap(
        card["skills_required_list"], user_state["skill_weights"]
    )
    skill_gain_score, _, _ = weighted_skill_overlap(
        card["skills_gained_list"], user_state["skill_weights"]
    )
    freshness_alignment_score = clamp(
        card["recency_score"] * user_state["freshness_preference"], 0.0, 1.0
    )
    source_loyalty_score = clamp(
        source_weight(user_state["source_loyalty_weights"], card["source_name"]) / 1.45,
        0.0,
        1.0,
    )
    breaking_affinity_score = clamp(
        card["breaking_score"] * user_state["breaking_affinity"], 0.0, 1.0
    )
    quality_blend = (
        0.3 * card["quality_score"]
        + 0.16 * card["popularity_score"]
        + 0.14 * card["editorial_priority"]
        + 0.2 * card["source_authority"]
        + 0.2 * card["topic_urgency"]
    )
    diversity_penalty = 0.0
    if recent_history:
        same_category_count = sum(
            1 for item in recent_history[-5:] if item["news_category"] == card["news_category"]
        )
        same_source_count = sum(
            1 for item in recent_history[-5:] if item["source_name"] == card["source_name"]
        )
        diversity_penalty = min(0.25, same_category_count * 0.045 + same_source_count * 0.05)

    selection_score = (
        1.4 * retrieval_similarity
        + 1.45 * topic_overlap_score
        + 1.6 * skill_overlap_score
        + 0.8 * skill_gain_score
        + 1.7 * freshness_alignment_score
        + 0.65 * source_loyalty_score
        + 0.6 * breaking_affinity_score
        + 0.7 * quality_blend
        - diversity_penalty
    )

    recent_window = recent_history[-8:]
    recent_open_rate = mean([item["open"] for item in recent_window]) if recent_window else 0.0
    recent_like_rate = mean([item["like"] for item in recent_window]) if recent_window else 0.0
    recent_share_rate = mean([item["share"] for item in recent_window]) if recent_window else 0.0
    recent_skip_rate = mean([item["skip_fast"] for item in recent_window]) if recent_window else 0.0
    category_entropy = entropy([item["news_category"] for item in recent_history[-10:]])
    session_depth_mean = mean([item["session_depth"] for item in recent_window]) if recent_window else 0.0

    return {
        "user_embedding": user_embedding,
        "retrieval_similarity": round(retrieval_similarity, 6),
        "topic_overlap_score": round(topic_overlap_score, 6),
        "skill_overlap_score": round(skill_overlap_score, 6),
        "skill_gain_score": round(skill_gain_score, 6),
        "interest_weight_mean": round(interest_weight_mean, 6),
        "skill_weight_mean": round(skill_weight_mean, 6),
        "interest_match_count": interest_match_count,
        "skill_match_count": skill_match_count,
        "format_match": format_match(user_state["preferred_formats"], card["format"]),
        "language_match": language_match(user_state["preferred_language"], card["language"]),
        "region_match": region_match(user_state["region"], card["location"]),
        "freshness_alignment_score": round(freshness_alignment_score, 6),
        "source_loyalty_score": round(source_loyalty_score, 6),
        "breaking_affinity_score": round(breaking_affinity_score, 6),
        "quality_blend": round(quality_blend, 6),
        "selection_score": selection_score,
        "recent_open_rate": round(recent_open_rate, 6),
        "recent_like_rate": round(recent_like_rate, 6),
        "recent_share_rate": round(recent_share_rate, 6),
        "recent_skip_rate": round(recent_skip_rate, 6),
        "category_entropy": round(category_entropy, 6),
        "session_depth_mean": round(session_depth_mean, 6),
    }


def sample_reaction(rng: random.Random, card: dict, features: dict) -> dict:
    open_prob = sigmoid(
        -1.05
        + 1.8 * features["retrieval_similarity"]
        + 1.25 * features["topic_overlap_score"]
        + 1.35 * features["freshness_alignment_score"]
        + 0.35 * features["source_loyalty_score"]
        + 0.2 * card["quality_score"]
    )
    open_flag = 1 if rng.random() < open_prob else 0

    like_prob = sigmoid(
        -1.35
        + 0.45 * open_flag
        + 1.15 * features["topic_overlap_score"]
        + 1.0 * features["skill_overlap_score"]
        + 0.95 * features["freshness_alignment_score"]
        + 0.45 * card["actionability_relevance"]
    )
    like_flag = 1 if rng.random() < like_prob else 0

    share_prob = sigmoid(
        -1.9
        + 0.75 * like_flag
        + 0.55 * card["topic_urgency"]
        + 0.55 * card["source_authority"]
        + 0.55 * card["breaking_score"]
        + 0.35 * card["actionability_relevance"]
    )
    share_flag = 1 if rng.random() < share_prob else 0

    long_view_prob = sigmoid(
        -1.2
        + 0.7 * open_flag
        + 0.95 * card["quality_score"]
        + 0.7 * features["topic_overlap_score"]
        + 0.3 * card["actionability_relevance"]
        + 0.25 * card["recency_score"]
    )
    long_view_flag = 1 if rng.random() < long_view_prob else 0

    skip_fast_prob = sigmoid(
        -0.15
        - 1.5 * features["topic_overlap_score"]
        - 1.05 * features["skill_overlap_score"]
        - 1.2 * features["freshness_alignment_score"]
        - 0.45 * features["source_loyalty_score"]
        + 0.7 * (1.0 - card["quality_score"])
        - 0.35 * open_flag
        - 0.35 * long_view_flag
    )
    skip_fast_flag = 1 if rng.random() < skip_fast_prob else 0

    disengage_prob = sigmoid(
        -0.4
        - 0.55 * open_flag
        - 0.35 * like_flag
        - 0.85 * features["freshness_alignment_score"]
        + 0.65 * (1.0 - card["quality_score"])
        + 0.25 * skip_fast_flag
    )
    disengage_flag = 1 if rng.random() < disengage_prob else 0

    dwell_time = int(
        clamp(
            8
            + 22 * open_flag
            + 17 * like_flag
            + 21 * long_view_flag
            + 12 * share_flag
            - 14 * skip_fast_flag
            - 9 * disengage_flag
            + 16 * features["topic_overlap_score"]
            + 12 * features["freshness_alignment_score"]
            + rng.uniform(-5, 8),
            3,
            180,
        )
    )

    return {
        "open": open_flag,
        "like": like_flag,
        "share": share_flag,
        "long_view": long_view_flag,
        "skip_fast": skip_fast_flag,
        "disengage": disengage_flag,
        "dwell_time_seconds": dwell_time,
    }


def apply_feedback(user_state: dict, card: dict, reaction: dict) -> None:
    positive_strength = (
        reaction["open"] * 0.05
        + reaction["like"] * 0.08
        + reaction["share"] * 0.1
        + reaction["long_view"] * 0.07
    )
    negative_strength = reaction["skip_fast"] * 0.07 + reaction["disengage"] * 0.09
    total_delta = positive_strength - negative_strength

    for topic in card["topics_list"]:
        current = user_state["interest_weights"].get(topic, 0.65)
        updated = clamp(current + total_delta, MIN_WEIGHT, MAX_WEIGHT)
        user_state["interest_weights"][topic] = round(updated, 4)

    for skill in card["skills_required_list"]:
        current = user_state["skill_weights"].get(skill, 0.7)
        updated = clamp(current + total_delta * 1.15, MIN_WEIGHT, MAX_WEIGHT)
        user_state["skill_weights"][skill] = round(updated, 4)

    for skill in card["skills_gained_list"]:
        current = user_state["skill_weights"].get(skill, 0.65)
        updated = clamp(current + total_delta * 0.8, MIN_WEIGHT, MAX_WEIGHT)
        user_state["skill_weights"][skill] = round(updated, 4)


def build_datasets(
    rng: random.Random,
    users_internal: dict[str, dict],
    cards_internal: dict[str, dict],
) -> tuple[list[dict], list[dict]]:
    interactions: list[dict] = []
    ranker_rows: list[dict] = []

    cards_list = list(cards_internal.values())

    for user_id, original_user in users_internal.items():
        recent_history: list[dict] = []
        recent_positive_embeddings: deque[list[float]] = deque(maxlen=5)
        mutable_user_state = {
            "interest_weights": dict(original_user["interest_weights"]),
            "skill_weights": dict(original_user["skill_weights"]),
            "preferred_language": original_user["preferred_language"],
            "region": original_user["region"],
            "preferred_formats": list(original_user["preferred_formats"]),
            "freshness_preference": original_user["freshness_preference"],
            "breaking_affinity": original_user["breaking_affinity"],
            "source_loyalty_weights": dict(original_user["source_loyalty_weights"]),
        }

        session_base_time = NOW - timedelta(days=rng.randint(5, 60), hours=rng.randint(0, 18))
        interaction_counter = 0

        for session_idx in range(1, SESSIONS_PER_USER + 1):
            session_id = f"{user_id}_session_{session_idx:03d}"
            session_depth = rng.randint(*SESSION_DEPTH_RANGE)
            shown_ids: set[str] = set()

            for depth_idx in range(1, session_depth + 1):
                user_embedding = current_user_embedding(
                    mutable_user_state["interest_weights"],
                    mutable_user_state["skill_weights"],
                    list(recent_positive_embeddings),
                )
                candidate_pool = [
                    card
                    for card in rng.sample(cards_list, k=min(45, len(cards_list)))
                    if card["status"] == "active" and card["card_id"] not in shown_ids
                ]
                if not candidate_pool:
                    candidate_pool = [card for card in cards_list if card["card_id"] not in shown_ids]

                scored_candidates = []
                for card in candidate_pool:
                    live_features = compute_live_features(
                        mutable_user_state,
                        card,
                        recent_history,
                        user_embedding,
                        depth_idx,
                    )
                    scored_candidates.append((live_features["selection_score"], {"card": card, "features": live_features}))

                chosen = choose_weighted(rng, scored_candidates)
                card = chosen["card"]
                features = chosen["features"]
                shown_ids.add(card["card_id"])

                shown_at = session_base_time + timedelta(minutes=interaction_counter * 9 + depth_idx * 3)
                interaction_counter += 1

                reaction = sample_reaction(rng, card, features)
                interaction_row = {
                    "user_id": user_id,
                    "card_id": card["card_id"],
                    "session_id": session_id,
                    "session_depth": depth_idx,
                    "shown_at": iso(shown_at),
                    "pool_type": "news",
                    "topic_overlap": features["interest_match_count"],
                    "skill_overlap": features["skill_match_count"],
                    "open": reaction["open"],
                    "like": reaction["like"],
                    "share": reaction["share"],
                    "long_view": reaction["long_view"],
                    "skip_fast": reaction["skip_fast"],
                    "disengage": reaction["disengage"],
                    "dwell_time_seconds": reaction["dwell_time_seconds"],
                }
                interactions.append(interaction_row)

                ranker_row = {
                    "user_id": user_id,
                    "card_id": card["card_id"],
                    "card_type": "news",
                    "news_category": card["news_category"],
                    "quality_score": card["quality_score"],
                    "popularity_score": card["popularity_score"],
                    "editorial_priority": card["editorial_priority"],
                    "source_authority": card["source_authority"],
                    "topic_urgency": card["topic_urgency"],
                    "actionability_relevance": card["actionability_relevance"],
                    "recency_score": card["recency_score"],
                    "breaking_score": card["breaking_score"],
                    "novelty_score": card["novelty_score"],
                    "integrity_score": card["integrity_score"],
                    "estimated_read_time_minutes": card["estimated_read_time_minutes"],
                    "retrieval_similarity": features["retrieval_similarity"],
                    "topic_overlap_score": features["topic_overlap_score"],
                    "skill_overlap_score": features["skill_overlap_score"],
                    "skill_gain_score": features["skill_gain_score"],
                    "interest_weight_mean": features["interest_weight_mean"],
                    "skill_weight_mean": features["skill_weight_mean"],
                    "interest_match_count": features["interest_match_count"],
                    "skill_match_count": features["skill_match_count"],
                    "format_match": features["format_match"],
                    "language_match": features["language_match"],
                    "region_match": features["region_match"],
                    "freshness_alignment_score": features["freshness_alignment_score"],
                    "source_loyalty_score": features["source_loyalty_score"],
                    "breaking_affinity_score": features["breaking_affinity_score"],
                    "recent_open_rate": features["recent_open_rate"],
                    "recent_like_rate": features["recent_like_rate"],
                    "recent_share_rate": features["recent_share_rate"],
                    "recent_skip_rate": features["recent_skip_rate"],
                    "category_entropy": features["category_entropy"],
                    "session_depth_mean": features["session_depth_mean"],
                }
                for idx in range(EMBED_DIM):
                    ranker_row[f"user_emb_{idx}"] = features["user_embedding"][idx]
                for idx in range(EMBED_DIM):
                    ranker_row[f"card_emb_{idx}"] = card["embedding"][idx]
                for label_name in ["open", "like", "share", "long_view", "skip_fast", "disengage"]:
                    ranker_row[label_name] = reaction[label_name]
                ranker_rows.append(ranker_row)

                history_row = {
                    **interaction_row,
                    "news_category": card["news_category"],
                    "source_name": card["source_name"],
                }
                recent_history.append(history_row)
                if reaction["open"] or reaction["like"] or reaction["share"] or reaction["long_view"]:
                    recent_positive_embeddings.append(card["embedding"])

                apply_feedback(mutable_user_state, card, reaction)

    interactions.sort(key=lambda item: (item["shown_at"], item["user_id"], item["card_id"]))
    ranker_rows.sort(key=lambda item: (item["user_id"], item["card_id"], item["recency_score"]), reverse=False)
    return interactions, ranker_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rng = random.Random(SEED)
    users_rows, users_internal = generate_users(rng)
    cards_rows, cards_internal = build_news_cards(rng)
    interactions_rows, ranker_rows = build_datasets(rng, users_internal, cards_internal)

    write_csv(RAW_DIR / "students.csv", users_rows)
    write_csv(RAW_DIR / "news.csv", cards_rows)
    write_csv(RAW_DIR / "interactions.csv", interactions_rows)
    write_csv(PROCESSED_DIR / "news_ranker_training.csv", ranker_rows)

    print(
        json.dumps(
            {
                "users": len(users_rows),
                "cards": len(cards_rows),
                "interactions": len(interactions_rows),
                "ranker_rows": len(ranker_rows),
                "generated_at": iso(NOW),
            },
            ensure_ascii=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
