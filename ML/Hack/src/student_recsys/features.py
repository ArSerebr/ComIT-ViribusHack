from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd


def split_pipe(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [part for part in str(value).split("|") if part]


def parse_embedding(value: Any, default_dim: int | None = None) -> list[float]:
    if isinstance(value, list):
        return [float(v) for v in value]
    if value is None or value == "":
        return [0.0] * default_dim if default_dim else []
    parsed = json.loads(value)
    return [float(v) for v in parsed]


def parse_weight_map(value: Any) -> dict[str, float]:
    if value is None or value == "" or (isinstance(value, float) and np.isnan(value)):
        return {}
    if isinstance(value, dict):
        return {str(key): float(weight) for key, weight in value.items()}
    parsed = json.loads(value)
    return {str(key): float(weight) for key, weight in parsed.items()}


def safe_mean(series: pd.Series) -> float:
    return float(series.mean()) if not series.empty else 0.0


def build_user_embedding(user_row: pd.Series, interactions: pd.DataFrame, cards: pd.DataFrame) -> np.ndarray:
    embedding_dim = default_dim_from_cards(cards)
    if embedding_dim == 0:
        return np.array([], dtype=float)
    vector = np.zeros(embedding_dim, dtype=float)
    interest_weights = parse_weight_map(user_row.get("interest_weights"))
    skill_weights = parse_weight_map(user_row.get("skill_weights"))
    user_topics = set(split_pipe(user_row.get("interests")))
    user_skills = set(split_pipe(user_row.get("skills")))

    card_scores: list[tuple[float, np.ndarray]] = []
    for _, card in cards.iterrows():
        card_embedding = np.array(parse_embedding(card.get("embedding_vector"), default_dim=embedding_dim), dtype=float)
        if card_embedding.size == 0:
            continue
        topic_matches = user_topics & set(split_pipe(card.get("topics")))
        skill_matches = user_skills & set(split_pipe(card.get("skills_required")))
        score = sum(interest_weights.get(tag, 0.0) for tag in topic_matches)
        score += 1.35 * sum(skill_weights.get(tag, 0.0) for tag in skill_matches)
        if score > 0.0:
            card_scores.append((float(score), card_embedding))

    for score, embedding in sorted(card_scores, key=lambda item: item[0], reverse=True)[:12]:
        vector += embedding * score

    user_id = user_row["user_id"] if "user_id" in user_row.index else str(user_row.name)
    history = interactions[interactions["user_id"] == user_id].tail(12)
    if not history.empty:
        card_vectors = history.merge(cards[["card_id", "embedding_vector"]], on="card_id", how="left")[
            "embedding_vector"
        ].apply(lambda value: parse_embedding(value, default_dim=embedding_dim))
        for idx, emb in enumerate(card_vectors):
            weight = 1.4 if history.iloc[idx]["like"] else 1.0
            weight += 0.8 if history.iloc[idx]["share"] else 0.0
            weight += 0.3 if history.iloc[idx]["open"] else 0.0
            weight += 0.4 if history.iloc[idx]["long_view"] else 0.0
            weight -= 0.9 if history.iloc[idx]["skip_fast"] else 0.0
            weight -= 1.1 if history.iloc[idx]["disengage"] else 0.0
            vector += np.array(emb, dtype=float) * weight

    if not np.any(vector):
        sample = cards["embedding_vector"].dropna()
        if not sample.empty:
            vector = np.array(parse_embedding(sample.iloc[0], default_dim=embedding_dim), dtype=float)
    norm = np.linalg.norm(vector) or 1.0
    return vector / norm


def default_dim_from_cards(cards: pd.DataFrame) -> int:
    if "embedding_vector" not in cards.columns or cards.empty:
        return 0
    for value in cards["embedding_vector"]:
        parsed = parse_embedding(value)
        if parsed:
            return len(parsed)
    return 0


def weighted_tag_match(weight_map: dict[str, float], tags: set[str]) -> float:
    if not tags:
        return 0.0
    if not weight_map:
        return 0.0
    matched_weight = sum(weight_map.get(tag, 0.0) for tag in tags)
    normalizer = sum(weight_map.values()) or 1.0
    return matched_weight / normalizer


def compute_overlap_features(user_row: pd.Series, card_row: pd.Series) -> dict[str, float]:
    user_interests = set(split_pipe(user_row["interests"]))
    user_skills = set(split_pipe(user_row["skills"]))
    interest_weights = parse_weight_map(user_row.get("interest_weights"))
    skill_weights = parse_weight_map(user_row.get("skill_weights"))
    topics = set(split_pipe(card_row["topics"]))
    required = set(split_pipe(card_row["skills_required"]))
    gained = set(split_pipe(card_row["skills_gained"]))
    weighted_topic_overlap = weighted_tag_match(interest_weights, topics)
    weighted_skill_overlap = weighted_tag_match(skill_weights, required)
    weighted_skill_gain = weighted_tag_match(skill_weights, gained)
    return {
        "topic_overlap_score": weighted_topic_overlap,
        "skill_overlap_score": weighted_skill_overlap,
        "skill_gain_score": weighted_skill_gain,
        "interest_weight_mean": safe_mean(pd.Series(list(interest_weights.values()))),
        "skill_weight_mean": safe_mean(pd.Series(list(skill_weights.values()))),
        "interest_match_count": len(user_interests & topics),
        "skill_match_count": len(user_skills & required),
        "format_match": float(card_row["format"] in split_pipe(user_row["preferred_formats"])),
        "language_match": float(card_row["language"] == user_row["preferred_language"]),
        "region_match": float(card_row["location"] == user_row["region"]),
        "difficulty_match": float(
            (user_row["experience_level"] in {"mid", "senior"} and card_row["difficulty_level"] != "beginner")
            or (user_row["experience_level"] in {"newcomer", "junior"} and card_row["difficulty_level"] != "advanced")
        ),
        "opportunity_readiness_score": min(1.0, 0.65 * weighted_skill_overlap + 0.35 * weighted_skill_gain),
    }


def build_user_behavior_features(user_id: str, interactions: pd.DataFrame) -> dict[str, float]:
    history = interactions[interactions["user_id"] == user_id].sort_values("shown_at")
    recent = history.tail(8)
    if history.empty:
        return {
            "recent_open_rate": 0.0,
            "recent_like_rate": 0.0,
            "recent_share_rate": 0.0,
            "recent_skip_rate": 0.0,
            "pool_entropy": 0.0,
            "session_depth_mean": 0.0,
        }
    pool_distribution = history["pool_type"].value_counts(normalize=True)
    entropy = float(-(pool_distribution * np.log2(pool_distribution + 1e-9)).sum())
    return {
        "recent_open_rate": safe_mean(recent["open"]),
        "recent_like_rate": safe_mean(recent["like"]),
        "recent_share_rate": safe_mean(recent["share"]),
        "recent_skip_rate": safe_mean(recent["skip_fast"]),
        "pool_entropy": entropy,
        "session_depth_mean": safe_mean(history["session_depth"]),
    }
