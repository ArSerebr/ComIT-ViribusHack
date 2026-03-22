import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from student_recsys.pipeline import RecommendationService

REACTION_POOL = {
    "open": "open detail page",
    "like": "like card",
    "share": "share card",
    "long_view": "long dwell time",
    "skip_fast": "fast skip",
    "disengage": "negative reaction",
}

REACTION_ALIASES = {
    "o": "open",
    "l": "like",
    "s": "share",
    "v": "long_view",
    "k": "skip_fast",
    "d": "disengage",
}


def _pipe_to_text(value: object) -> str:
    if value is None:
        return "-"
    text = str(value)
    if not text or text == "nan":
        return "-"
    return ", ".join(part for part in text.split("|") if part)


def _line(label: str, value: object) -> str:
    return f"{label:<22}: {value}"


def _render_profile(snapshot: dict[str, list[tuple[str, float]]]) -> str:
    interest_text = ", ".join(f"{name} ({weight:.2f})" for name, weight in snapshot["interests"]) or "-"
    skill_text = ", ".join(f"{name} ({weight:.2f})" for name, weight in snapshot["skills"]) or "-"
    return "\n".join(
        [
            "USER PROFILE STATE",
            _line("Top interests", interest_text),
            _line("Top skills", skill_text),
            "-" * 88,
        ]
    )


def _render_card(card: dict[str, object], position: int) -> str:
    content_lines = [
        "=" * 88,
        f"CARD {position}",
        "-" * 88,
        "CARD CONTENT",
        _line("Title", card["title"]),
        _line("Type", card["card_type"]),
        _line("Short description", card["short_description"]),
        _line("Full description", card["full_description"]),
        _line("Topics", _pipe_to_text(card["topics"])),
        _line("Skills required", _pipe_to_text(card["skills_required"])),
        _line("Skills gained", _pipe_to_text(card["skills_gained"])),
        _line("Difficulty", card["difficulty_level"]),
        _line("Format", card["format"]),
        _line("Language", card["language"]),
        _line("Location", card["location"]),
        _line("Start date", card["start_date"]),
        _line("End date", card["end_date"]),
        _line("Deadline", card["application_deadline"]),
        _line("Duration", f"{card['estimated_duration']} days"),
        _line("Team based", "yes" if int(card["team_based"]) else "no"),
        _line("Organization", card["host_organization"]),
        _line("Cost", card["cost_type"]),
        _line("Reward", card["reward_type"]),
        _line("Eligibility", card["eligibility_constraints"]),
        "",
        "MODEL SIGNALS",
        _line("Retrieval strategy", card["retrieval_strategy"]),
        _line("Retrieval reason", card["retrieval_reason"]),
        _line("Retrieval similarity", f"{float(card['retrieval_similarity']):.4f}"),
        _line("Quality score", f"{float(card['quality_score']):.4f}"),
        _line("Popularity score", f"{float(card['popularity_score']):.4f}"),
        _line("Novelty score", f"{float(card['novelty_score']):.4f}"),
        _line("Diversity score", f"{float(card['diversity_contribution']):.4f}"),
        _line("Penalty", f"{float(card['soft_filter_penalty']):.4f}"),
        _line("P(open)", f"{float(card['p_open']):.4f}"),
        _line("P(like)", f"{float(card['p_like']):.4f}"),
        _line("P(share)", f"{float(card['p_share']):.4f}"),
        _line("P(long_view)", f"{float(card['p_long_view']):.4f}"),
        _line("P(skip_fast)", f"{float(card['p_skip_fast']):.4f}"),
        _line("P(disengage)", f"{float(card['p_disengage']):.4f}"),
        _line("Final score", f"{float(card['adjusted_final_score']):.4f}"),
        "=" * 88,
    ]
    return "\n".join(content_lines)


def _read_reaction() -> str:
    print("Available reactions:")
    for key, label in REACTION_POOL.items():
        print(f"  - {key:<10} ({label})")
    print("  - q          (quit)")
    while True:
        raw_value = input("Reaction > ").strip().lower()
        if raw_value == "q":
            return "q"
        reaction = REACTION_ALIASES.get(raw_value, raw_value)
        if reaction in REACTION_POOL:
            return reaction
        print("Unknown reaction. Use one of the listed values.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run interactive recommendation feed for a user.")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--max-cards", type=int, default=10)
    args = parser.parse_args()

    root = ROOT
    service = RecommendationService(root)
    print(f"Interactive recommendation feed for {args.user_id}")
    print("Each reaction is written into interaction history and affects the next recommendation.\n")

    for position in range(1, args.max_cards + 1):
        profile_snapshot = service.get_user_profile_snapshot(args.user_id)
        feed = service.recommend(args.user_id)
        if feed.empty:
            print("No more eligible recommendations for this user.")
            break
        current_card = feed.iloc[0].to_dict()
        print(_render_profile(profile_snapshot))
        print(_render_card(current_card, position))
        reaction = _read_reaction()
        if reaction == "q":
            print("Feed session finished.")
            break
        service.update_feedback(args.user_id, str(current_card["card_id"]), reaction)
        updated_snapshot = service.get_user_profile_snapshot(args.user_id)
        print(f"Saved reaction `{reaction}` for `{current_card['title']}`.")
        print(_render_profile(updated_snapshot))
        print()
