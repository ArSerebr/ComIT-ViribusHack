from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
TRAINING_PATH = BASE_DIR / "data" / "processed" / "news_ranker_training.csv"
MODEL_PATH = BASE_DIR / "models" / "reaction_update_model.json"

ACTION_CONFIG = {
    "viewed": {"label": "open", "multiplier": 0.72},
    "liked": {"label": "like", "multiplier": 1.0},
    "read_more": {"label": "long_view", "multiplier": 1.12},
}

FEATURES = [
    "topic_overlap_score",
    "skill_overlap_score",
    "skill_gain_score",
    "freshness_alignment_score",
    "source_loyalty_score",
    "breaking_affinity_score",
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def round4(value: float) -> float:
    return round(value, 4)


def train_model() -> dict:
    aggregates = {
        action_name: {
            "rows": 0,
            "positives": 0,
            **{feature: 0.0 for feature in FEATURES},
        }
        for action_name in ACTION_CONFIG
    }

    with TRAINING_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for action_name, config in ACTION_CONFIG.items():
                bucket = aggregates[action_name]
                bucket["rows"] += 1
                label_value = int(row[config["label"]])
                if label_value != 1:
                    continue
                bucket["positives"] += 1
                for feature in FEATURES:
                    bucket[feature] += float(row[feature])

    model = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_file": str(TRAINING_PATH),
        "actions": {},
        "limits": {
            "min_interest_weight": 0.2,
            "max_interest_weight": 2.2,
            "min_skill_weight": 0.2,
            "max_skill_weight": 2.2,
            "new_topic_cold_start": 0.62,
            "new_skill_cold_start": 0.64,
        },
    }

    for action_name, config in ACTION_CONFIG.items():
        bucket = aggregates[action_name]
        positives = max(bucket["positives"], 1)
        positive_rate = bucket["positives"] / max(bucket["rows"], 1)
        topic_mean = bucket["topic_overlap_score"] / positives
        skill_mean = bucket["skill_overlap_score"] / positives
        gain_mean = bucket["skill_gain_score"] / positives
        freshness_mean = bucket["freshness_alignment_score"] / positives
        source_mean = bucket["source_loyalty_score"] / positives
        breaking_mean = bucket["breaking_affinity_score"] / positives
        multiplier = config["multiplier"]

        # Online updates should stay stable, but interests should move
        # noticeably enough to change the next few recommendations.
        interest_delta = clamp(
            0.0046 + positive_rate * 0.0042 + topic_mean * 0.0115 * multiplier,
            0.004,
            0.026,
        )
        required_skill_delta = clamp(
            0.0034 + positive_rate * 0.003 + skill_mean * 0.0085 * multiplier,
            0.003,
            0.019,
        )
        gained_skill_delta = clamp(
            0.0026 + positive_rate * 0.002 + gain_mean * 0.0065 * multiplier,
            0.0025,
            0.015,
        )
        freshness_delta = clamp(
            0.0015 + freshness_mean * 0.0045 * multiplier,
            0.001,
            0.01,
        )
        source_delta = clamp(
            0.001 + source_mean * 0.0038 * multiplier,
            0.001,
            0.008,
        )
        breaking_delta = clamp(
            0.001 + breaking_mean * 0.0032 * multiplier,
            0.001,
            0.008,
        )

        model["actions"][action_name] = {
            "trained_from_label": config["label"],
            "positive_rate": round4(positive_rate),
            "feature_means": {
                "topic_overlap_score": round4(topic_mean),
                "skill_overlap_score": round4(skill_mean),
                "skill_gain_score": round4(gain_mean),
                "freshness_alignment_score": round4(freshness_mean),
                "source_loyalty_score": round4(source_mean),
                "breaking_affinity_score": round4(breaking_mean),
            },
            "interest_delta": round4(interest_delta),
            "required_skill_delta": round4(required_skill_delta),
            "gained_skill_delta": round4(gained_skill_delta),
            "freshness_delta": round4(freshness_delta),
            "source_delta": round4(source_delta),
            "breaking_delta": round4(breaking_delta),
            "redistribution_share": round4(
                clamp(0.24 + multiplier * 0.09, 0.26, 0.36)
            ),
        }

    return model


def main() -> None:
    model = train_model()
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MODEL_PATH.open("w", encoding="utf-8") as handle:
        json.dump(model, handle, ensure_ascii=True, indent=2)
    print(json.dumps(model, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
