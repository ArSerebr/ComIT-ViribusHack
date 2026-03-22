from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path

from gigachat_embedding_provider import embed_weighted_tokens


BASE_DIR = Path(__file__).resolve().parent
USERS_PATH = BASE_DIR / "data" / "raw" / "students.csv"
CARDS_PATH = BASE_DIR / "data" / "raw" / "news.csv"
INTERACTIONS_PATH = BASE_DIR / "data" / "raw" / "interactions.csv"
NOW = datetime(2026, 3, 22, 12, 0, 0)
def parse_pipe(value: str) -> list[str]:
    if not value:
        return []
    return [item for item in value.split("|") if item]


def parse_json(value: str) -> object:
    return json.loads(value) if value else {}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_embedding(weighted_tokens: list[tuple[str, float]]) -> list[float]:
    return embed_weighted_tokens(weighted_tokens)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return clamp(numerator / (norm_a * norm_b), -1.0, 1.0)


def load_users() -> dict[str, dict]:
    users: dict[str, dict] = {}
    with USERS_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            users[row["user_id"]] = {
                **row,
                "interests_list": parse_pipe(row["interests"]),
                "skills_list": parse_pipe(row["skills"]),
                "preferred_formats_list": parse_pipe(row["preferred_formats"]),
                "interest_weights_map": parse_json(row["interest_weights"]),
                "skill_weights_map": parse_json(row["skill_weights"]),
                "source_loyalty_weights_map": parse_json(row["source_loyalty_weights"]),
                "freshness_preference": float(row["freshness_preference"]),
                "breaking_affinity": float(row["breaking_affinity"]),
            }
    return users


def load_cards() -> list[dict]:
    cards: list[dict] = []
    with CARDS_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row["topics_list"] = parse_pipe(row["topics"])
            row["skills_required_list"] = parse_pipe(row["skills_required"])
            row["skills_gained_list"] = parse_pipe(row["skills_gained"])
            row["embedding"] = parse_json(row["embedding_vector"])
            for field in [
                "quality_score",
                "popularity_score",
                "editorial_priority",
                "source_authority",
                "topic_urgency",
                "actionability_relevance",
                "recency_score",
                "breaking_score",
                "novelty_score",
                "integrity_score",
            ]:
                row[field] = float(row[field])
            row["estimated_read_time_minutes"] = int(row["estimated_read_time_minutes"])
            row["updated_dt"] = datetime.fromisoformat(row["updated_at"])
            cards.append(row)
    return cards


def load_recent_interactions(user_id: str, lookback: int = 20) -> list[dict]:
    rows: list[dict] = []
    with INTERACTIONS_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row["user_id"] != user_id:
                continue
            row["shown_dt"] = datetime.fromisoformat(row["shown_at"])
            rows.append(row)
    rows.sort(key=lambda item: item["shown_dt"], reverse=True)
    return rows[:lookback]


def weighted_overlap(tokens: list[str], weight_map: dict[str, float]) -> tuple[float, float, int]:
    matched = [float(weight_map[token]) for token in tokens if token in weight_map]
    if not matched:
        return 0.0, 0.0, 0
    matched_mean = mean(matched)
    return clamp(matched_mean / 1.8, 0.0, 1.0), matched_mean, len(matched)


def build_user_embedding(user: dict) -> list[float]:
    weighted_tokens: list[tuple[str, float]] = []
    for topic, weight in user["interest_weights_map"].items():
        weighted_tokens.append((f"topic::{topic}", float(weight)))
    for skill, weight in user["skill_weights_map"].items():
        weighted_tokens.append((f"skill::{skill}", float(weight) * 1.25))
    return build_embedding(weighted_tokens)


def score_card(user: dict, card: dict, recent_interactions: list[dict]) -> dict | None:
    if card["status"] != "active":
        return None
    if card["integrity_score"] < 0.72:
        return None
    if card["recency_score"] < 0.15:
        return None

    recent_card_ids = {row["card_id"] for row in recent_interactions[:12]}
    if card["card_id"] in recent_card_ids:
        return None

    user_embedding = build_user_embedding(user)
    retrieval_similarity = clamp(
        (cosine_similarity(user_embedding, card["embedding"]) + 1.0) / 2.0,
        0.0,
        1.0,
    )
    topic_overlap_score, interest_weight_mean, interest_match_count = weighted_overlap(
        card["topics_list"], user["interest_weights_map"]
    )
    skill_overlap_score, skill_weight_mean, skill_match_count = weighted_overlap(
        card["skills_required_list"], user["skill_weights_map"]
    )
    skill_gain_score, _, _ = weighted_overlap(
        card["skills_gained_list"], user["skill_weights_map"]
    )

    freshness_alignment_score = clamp(
        card["recency_score"] * user["freshness_preference"], 0.0, 1.0
    )
    source_loyalty_raw = float(user["source_loyalty_weights_map"].get(card["source_name"], 0.95))
    source_loyalty_score = clamp(source_loyalty_raw / 1.45, 0.0, 1.0)
    breaking_affinity_score = clamp(
        card["breaking_score"] * user["breaking_affinity"], 0.0, 1.0
    )

    format_match = 1.0 if card["format"] in user["preferred_formats_list"] else 0.0
    language_match = 1.0 if card["language"] == user["preferred_language"] else 0.0
    region_match = 1.0 if card["location"] in {user["region"], "Global"} else 0.0

    same_source_recent = sum(1 for row in recent_interactions[:10] if row.get("source_name") == card["source_name"])
    same_category_recent = sum(
        1 for row in recent_interactions[:10] if row.get("news_category") == card["news_category"]
    )
    same_topic_recent = sum(
        1
        for row in recent_interactions[:10]
        if set(row.get("topics", [])) & set(card["topics_list"])
    )
    repeated_source_penalty = min(0.18, same_source_recent * 0.05)
    repeated_category_penalty = min(0.14, same_category_recent * 0.04)
    repeated_topic_penalty = min(0.3, same_topic_recent * 0.06)

    quality_blend = (
        0.24 * card["quality_score"]
        + 0.12 * card["popularity_score"]
        + 0.12 * card["editorial_priority"]
        + 0.22 * card["source_authority"]
        + 0.16 * card["topic_urgency"]
        + 0.14 * card["actionability_relevance"]
    )

    final_score = (
        1.25 * retrieval_similarity
        + 1.45 * topic_overlap_score
        + 1.6 * skill_overlap_score
        + 0.75 * skill_gain_score
        + 1.8 * freshness_alignment_score
        + 0.65 * source_loyalty_score
        + 0.6 * breaking_affinity_score
        + 0.18 * format_match
        + 0.18 * language_match
        + 0.12 * region_match
        + 0.9 * quality_blend
        - repeated_source_penalty
        - repeated_category_penalty
        - repeated_topic_penalty
    )

    hours_since_update = max((NOW - card["updated_dt"]).total_seconds() / 3600.0, 0.0)
    why = []
    if topic_overlap_score >= 0.6:
        why.append("strong topic match")
    if skill_overlap_score >= 0.55:
        why.append("strong skill match")
    if freshness_alignment_score >= 0.8:
        why.append("very fresh for this user")
    if card["topic_urgency"] >= 0.75:
        why.append("high topic urgency")
    if card["source_authority"] >= 0.9:
        why.append("high-authority source")
    if not why:
        why.append("balanced relevance and freshness")

    return {
        "card_id": card["card_id"],
        "title": card["title"],
        "source_name": card["source_name"],
        "news_category": card["news_category"],
        "language": card["language"],
        "location": card["location"],
        "updated_at": card["updated_at"],
        "hours_since_update": round(hours_since_update, 2),
        "final_score": round(final_score, 4),
        "retrieval_similarity": round(retrieval_similarity, 4),
        "topic_overlap_score": round(topic_overlap_score, 4),
        "skill_overlap_score": round(skill_overlap_score, 4),
        "freshness_alignment_score": round(freshness_alignment_score, 4),
        "source_loyalty_score": round(source_loyalty_score, 4),
        "breaking_affinity_score": round(breaking_affinity_score, 4),
        "quality_blend": round(quality_blend, 4),
        "recency_score": round(card["recency_score"], 4),
        "topic_urgency": round(card["topic_urgency"], 4),
        "source_authority": round(card["source_authority"], 4),
        "topics": card["topics_list"],
        "why": why,
    }


def enrich_recent_interactions(recent_interactions: list[dict], cards_by_id: dict[str, dict]) -> None:
    for row in recent_interactions:
        card = cards_by_id.get(row["card_id"])
        if not card:
            continue
        row["source_name"] = card["source_name"]
        row["news_category"] = card["news_category"]
        row["topics"] = card["topics_list"]


def recommend_top_news(user_id: str, limit: int = 10) -> list[dict]:
    users = load_users()
    cards = load_cards()
    cards_by_id = {card["card_id"]: card for card in cards}

    if user_id not in users:
        raise ValueError(f"Unknown user_id: {user_id}")

    user = users[user_id]
    recent_interactions = load_recent_interactions(user_id)
    enrich_recent_interactions(recent_interactions, cards_by_id)

    scored = []
    for card in cards:
        result = score_card(user, card, recent_interactions)
        if result is not None:
            scored.append(result)

    scored.sort(
        key=lambda item: (
            item["final_score"],
            item["freshness_alignment_score"],
            item["retrieval_similarity"],
            item["source_authority"],
        ),
        reverse=True,
    )
    return scored[:limit]


def print_human_readable(recommendations: list[dict]) -> None:
    for idx, item in enumerate(recommendations, start=1):
        print(f"{idx}. {item['title']} [{item['card_id']}]")
        print(
            "   "
            f"score={item['final_score']} "
            f"freshness={item['freshness_alignment_score']} "
            f"match={item['retrieval_similarity']} "
            f"urgency={item['topic_urgency']} "
            f"source={item['source_name']}"
        )
        print(
            "   "
            f"updated={item['updated_at']} "
            f"topics={', '.join(item['topics'])} "
            f"why={', '.join(item['why'])}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend top personal news for a student user.")
    parser.add_argument("--user-id", required=True, help="User identifier from data/raw/students.csv")
    parser.add_argument("--limit", type=int, default=10, help="How many cards to return")
    parser.add_argument("--json", action="store_true", help="Print recommendations as JSON")
    args = parser.parse_args()

    recommendations = recommend_top_news(args.user_id, args.limit)
    if args.json:
        print(json.dumps(recommendations, ensure_ascii=True, indent=2))
        return
    print_human_readable(recommendations)


if __name__ == "__main__":
    main()
