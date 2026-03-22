from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta
from pathlib import Path

from recommender import (
    load_cards,
    load_recent_interactions,
    load_users,
    score_card,
    enrich_recent_interactions,
)


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "reaction_update_model.json"
NOW = datetime(2026, 3, 22, 12, 0, 0)

REACTION_MAP = {
    "1": "viewed",
    "2": "liked",
    "3": "read_more",
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def load_reaction_model() -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Reaction model not found. Run `py train_reaction_model.py` first."
        )
    with MODEL_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def top_weights(weight_map: dict[str, float], limit: int = 5) -> list[tuple[str, float]]:
    return sorted(
        ((key, float(value)) for key, value in weight_map.items()),
        key=lambda item: item[1],
        reverse=True,
    )[:limit]


def print_profile_snapshot(user_state: dict) -> None:
    interest_text = ", ".join(
        f"{name}:{value:.3f}" for name, value in top_weights(user_state["interest_weights_map"])
    )
    skill_text = ", ".join(
        f"{name}:{value:.3f}" for name, value in top_weights(user_state["skill_weights_map"])
    )
    print("Top interests:", interest_text)
    print("Top skills   :", skill_text)


def recommend_next(
    user_state: dict,
    cards: list[dict],
    recent_interactions: list[dict],
    shown_in_session: set[str],
) -> dict | None:
    scored = []
    for card in cards:
        if card["card_id"] in shown_in_session:
            continue
        result = score_card(user_state, card, recent_interactions)
        if result is not None:
            scored.append(result)
    if not scored:
        return None
    scored.sort(
        key=lambda item: (
            item["final_score"],
            item["freshness_alignment_score"],
            item["retrieval_similarity"],
            item["source_authority"],
        ),
        reverse=True,
    )
    return scored[0]


def redistribute_weights(
    weight_map: dict[str, float],
    matched_tokens: set[str],
    total_added: float,
    redistribution_share: float,
    min_weight: float,
    max_weight: float,
) -> None:
    if total_added <= 0:
        return
    untouched = [token for token in weight_map.keys() if token not in matched_tokens]
    if not untouched:
        return
    subtract_total = total_added * redistribution_share
    subtract_per_token = subtract_total / len(untouched)
    for token in untouched:
        weight_map[token] = round(
            clamp(float(weight_map[token]) - subtract_per_token, min_weight, max_weight),
            4,
        )


def apply_reaction_update(user_state: dict, card: dict, reaction_name: str, reaction_model: dict) -> None:
    action_cfg = reaction_model["actions"][reaction_name]
    limits = reaction_model["limits"]

    matched_topics = set(card["topics_list"])
    matched_required_skills = set(card["skills_required_list"])
    matched_gained_skills = set(card["skills_gained_list"])

    interest_delta = float(action_cfg["interest_delta"])
    required_skill_delta = float(action_cfg["required_skill_delta"])
    gained_skill_delta = float(action_cfg["gained_skill_delta"])
    redistribution_share = float(action_cfg["redistribution_share"])

    topic_boost_factor = 1.0 + 0.22 * float(card["topic_urgency"])
    skill_boost_factor = 0.85 + 0.15 * float(card["actionability_relevance"])

    total_interest_added = 0.0
    for topic in matched_topics:
        current = float(
            user_state["interest_weights_map"].get(topic, limits["new_topic_cold_start"])
        )
        updated = clamp(
            current + interest_delta * topic_boost_factor,
            limits["min_interest_weight"],
            limits["max_interest_weight"],
        )
        total_interest_added += updated - current
        user_state["interest_weights_map"][topic] = round(updated, 4)

    total_required_added = 0.0
    for skill in matched_required_skills:
        current = float(
            user_state["skill_weights_map"].get(skill, limits["new_skill_cold_start"])
        )
        updated = clamp(
            current + required_skill_delta * skill_boost_factor,
            limits["min_skill_weight"],
            limits["max_skill_weight"],
        )
        total_required_added += updated - current
        user_state["skill_weights_map"][skill] = round(updated, 4)

    total_gained_added = 0.0
    for skill in matched_gained_skills:
        current = float(
            user_state["skill_weights_map"].get(skill, limits["new_skill_cold_start"])
        )
        updated = clamp(
            current + gained_skill_delta,
            limits["min_skill_weight"],
            limits["max_skill_weight"],
        )
        total_gained_added += updated - current
        user_state["skill_weights_map"][skill] = round(updated, 4)

    redistribute_weights(
        user_state["interest_weights_map"],
        matched_topics,
        total_interest_added,
        redistribution_share,
        limits["min_interest_weight"],
        limits["max_interest_weight"],
    )
    redistribute_weights(
        user_state["skill_weights_map"],
        matched_required_skills | matched_gained_skills,
        total_required_added + total_gained_added,
        redistribution_share,
        limits["min_skill_weight"],
        limits["max_skill_weight"],
    )

    freshness_shift = float(action_cfg["freshness_delta"]) * (float(card["recency_score"]) - 0.35)
    breaking_shift = float(action_cfg["breaking_delta"]) * (float(card["breaking_score"]) - 0.25)
    source_shift = float(action_cfg["source_delta"]) * (float(card["source_authority"]) - 0.5)

    user_state["freshness_preference"] = round(
        clamp(float(user_state["freshness_preference"]) + freshness_shift, 0.75, 1.75),
        4,
    )
    user_state["breaking_affinity"] = round(
        clamp(float(user_state["breaking_affinity"]) + breaking_shift, 0.7, 1.75),
        4,
    )
    source_name = card["source_name"]
    current_source_weight = float(user_state["source_loyalty_weights_map"].get(source_name, 0.95))
    user_state["source_loyalty_weights_map"][source_name] = round(
        clamp(current_source_weight + source_shift, 0.75, 1.6),
        4,
    )


def append_session_interaction(
    recent_interactions: list[dict],
    card: dict,
    shown_at: datetime,
) -> None:
    recent_interactions.insert(
        0,
        {
            "card_id": card["card_id"],
            "shown_dt": shown_at,
            "source_name": card["source_name"],
            "news_category": card["news_category"],
            "topics": card["topics_list"],
        },
    )
    del recent_interactions[20:]


def print_recommendation(news_item: dict) -> None:
    print()
    print("Recommended news")
    print(f"Title : {news_item['title']}")
    print(f"ID    : {news_item['card_id']}")
    print(f"Topic : {', '.join(news_item['topics'])}")
    print(f"Why   : {', '.join(news_item['why'])}")
    print(
        "Score : "
        f"{news_item['final_score']} "
        f"(freshness={news_item['freshness_alignment_score']}, "
        f"match={news_item['retrieval_similarity']}, "
        f"urgency={news_item['topic_urgency']})"
    )


def main() -> None:
    reaction_model = load_reaction_model()
    users = load_users()
    cards = load_cards()
    cards_by_id = {card["card_id"]: card for card in cards}

    student_id = input("Enter student id: ").strip()
    if student_id not in users:
        available_sample = ", ".join(sorted(list(users.keys()))[:5])
        print(f"Unknown student id. Try one of: {available_sample}")
        return

    user_state = copy.deepcopy(users[student_id])
    recent_interactions = load_recent_interactions(student_id)
    enrich_recent_interactions(recent_interactions, cards_by_id)
    shown_in_session: set[str] = set()

    print()
    print(f"Real-time test started for {student_id}")
    print_profile_snapshot(user_state)

    turn = 0
    while True:
        turn += 1
        recommendation = recommend_next(
            user_state,
            cards,
            recent_interactions,
            shown_in_session,
        )
        if recommendation is None:
            print("No more suitable active news found for this session.")
            return

        card = cards_by_id[recommendation["card_id"]]
        shown_in_session.add(card["card_id"])
        print_recommendation(recommendation)
        print("Reaction: 1 = just viewed, 2 = liked, 3 = read more, q = quit")
        reaction_key = input("Your choice: ").strip().lower()
        if reaction_key == "q":
            print("Session finished.")
            return
        if reaction_key not in REACTION_MAP:
            print("Unknown reaction, try again.")
            shown_in_session.remove(card["card_id"])
            turn -= 1
            continue

        reaction_name = REACTION_MAP[reaction_key]
        before_interest_snapshot = top_weights(user_state["interest_weights_map"], limit=3)
        apply_reaction_update(user_state, card, reaction_name, reaction_model)
        shown_at = NOW + timedelta(minutes=turn * 3)
        append_session_interaction(recent_interactions, card, shown_at)

        after_interest_snapshot = top_weights(user_state["interest_weights_map"], limit=3)
        print()
        print(f"Applied reaction: {reaction_name}")
        print(
            "Interest weights shifted slightly "
            f"(freshness_preference={user_state['freshness_preference']}, "
            f"breaking_affinity={user_state['breaking_affinity']})"
        )
        print("Top interests before:", ", ".join(f"{k}:{v:.3f}" for k, v in before_interest_snapshot))
        print("Top interests after :", ", ".join(f"{k}:{v:.3f}" for k, v in after_interest_snapshot))
        print("-" * 72)


if __name__ == "__main__":
    main()
