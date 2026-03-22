from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import Ridge
from sklearn.metrics.pairwise import cosine_similarity

from .data_generation import load_settings
from .features import (
    build_user_behavior_features,
    build_user_embedding,
    compute_overlap_features,
    default_dim_from_cards,
    parse_embedding,
)
from .schema import Paths


TARGETS = ["open", "like", "share", "long_view", "skip_fast", "disengage"]


@dataclass(slots=True)
class TrainedArtifacts:
    retrieval: dict[str, Any]
    ranker: dict[str, Any]
    metadata: dict[str, Any]


def _prepare_ranker_dataset(
    users: pd.DataFrame,
    cards: pd.DataFrame,
    interactions: pd.DataFrame,
    user_embeddings: dict[str, list[float]],
    user_behaviors: dict[str, dict[str, float]],
) -> pd.DataFrame:
    user_lookup = users.set_index("user_id")
    card_lookup = cards.set_index("card_id")
    embedding_dim = default_dim_from_cards(cards)
    rows: list[dict[str, Any]] = []
    for _, event in interactions.iterrows():
        user = user_lookup.loc[event["user_id"]]
        card = card_lookup.loc[event["card_id"]]
        overlap = compute_overlap_features(user, card)
        behavior = user_behaviors[event["user_id"]]
        user_embedding = np.array(user_embeddings[event["user_id"]])
        candidate_embedding = np.array(parse_embedding(card["embedding_vector"], default_dim=embedding_dim))
        row = {
            "user_id": event["user_id"],
            "card_id": event["card_id"],
            "card_type": card["card_type"],
            "quality_score": float(card["quality_score"]),
            "popularity_score": float(card["popularity_score"]),
            "editorial_priority": float(card["editorial_priority"]),
            "integrity_score": float(card["integrity_score"]),
            "estimated_duration": float(card["estimated_duration"]),
            "team_based": float(card["team_based"]),
            "retrieval_similarity": float(cosine_similarity([user_embedding], [candidate_embedding])[0][0]),
        }
        row.update(overlap)
        row.update(behavior)
        for index, value in enumerate(user_embedding):
            row[f"user_emb_{index}"] = float(value)
        for index, value in enumerate(candidate_embedding):
            row[f"card_emb_{index}"] = float(value)
        for target in TARGETS:
            row[target] = int(event[target])
        rows.append(row)
    return pd.DataFrame(rows)


def train_models(root: Path) -> TrainedArtifacts:
    paths = Paths(root)
    settings = load_settings(root)
    users = pd.read_csv(paths.users_raw)
    cards = pd.read_csv(paths.cards_raw)
    interactions = pd.read_csv(paths.interactions_raw)
    cards.attrs["settings"] = settings
    embedding_dim = default_dim_from_cards(cards)

    user_embeddings = {}
    for _, user in users.iterrows():
        user_embeddings[user["user_id"]] = build_user_embedding(user, interactions, cards).tolist()
    user_behaviors = {
        user_id: build_user_behavior_features(user_id, interactions) for user_id in users["user_id"].tolist()
    }
    card_embeddings = {
        row["card_id"]: parse_embedding(row["embedding_vector"], default_dim=embedding_dim) for _, row in cards.iterrows()
    }

    ranker_dataset = _prepare_ranker_dataset(users, cards, interactions, user_embeddings, user_behaviors)
    ranker_dataset.to_csv(paths.ranked_training, index=False)

    feature_columns = [
        column
        for column in ranker_dataset.columns
        if column not in {"user_id", "card_id", "card_type", *TARGETS}
    ]
    X = pd.get_dummies(ranker_dataset[feature_columns], columns=[], drop_first=False)

    models = {}
    for target in TARGETS:
        if ranker_dataset[target].nunique() < 2:
            estimator = DummyClassifier(strategy="most_frequent")
        else:
            estimator = GradientBoostingClassifier(random_state=settings["random_seed"])
        estimator.fit(X, ranker_dataset[target])
        models[target] = estimator

    retrieval_projection = Ridge(alpha=1.0)
    retrieval_X = np.array(list(user_embeddings.values()))
    retrieval_y = np.array(
        [
            np.mean(
                [
                    card_embeddings[card_id]
                    for card_id in interactions[interactions["user_id"] == user_id]["card_id"].head(6).tolist()
                ],
                axis=0,
            )
            for user_id in user_embeddings
        ]
    )
    retrieval_projection.fit(retrieval_X, retrieval_y)

    retrieval_artifact = {
        "user_embeddings": user_embeddings,
        "card_embeddings": card_embeddings,
        "projection": retrieval_projection,
        "top_k_per_source": settings["retrieval"]["top_k_per_source"],
        "embedding_dim": embedding_dim,
    }
    ranker_artifact = {
        "models": models,
        "feature_columns": X.columns.tolist(),
        "targets": TARGETS,
    }
    metadata = {
        "settings": settings,
        "cards_columns": cards.columns.tolist(),
        "users_columns": users.columns.tolist(),
        "embedding_dim": embedding_dim,
    }

    joblib.dump(retrieval_artifact, paths.retrieval_model)
    joblib.dump(ranker_artifact, paths.ranker_model)
    joblib.dump(metadata, paths.metadata_model)
    return TrainedArtifacts(retrieval=retrieval_artifact, ranker=ranker_artifact, metadata=metadata)
