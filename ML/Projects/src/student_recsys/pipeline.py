from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .data_generation import load_settings
from .features import (
    build_user_behavior_features,
    build_user_embedding,
    compute_overlap_features,
    default_dim_from_cards,
    parse_embedding,
    parse_weight_map,
    split_pipe,
    weighted_tag_match,
)
from .schema import CARD_TYPES, Paths


@dataclass(slots=True)
class RecommendationService:
    root: Path
    paths: Paths = field(init=False)
    settings: dict[str, Any] = field(init=False)
    users: pd.DataFrame = field(init=False)
    cards: pd.DataFrame = field(init=False)
    interactions: pd.DataFrame = field(init=False)
    retrieval: dict[str, Any] = field(init=False)
    ranker: dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        self.paths = Paths(self.root)
        self.settings = load_settings(self.root)
        self.users = pd.read_csv(self.paths.users_raw)
        self.cards = pd.read_csv(self.paths.cards_raw)
        self.interactions = pd.read_csv(self.paths.interactions_raw)
        self.cards.attrs["settings"] = self.settings
        self.retrieval = joblib.load(self.paths.retrieval_model)
        self.ranker = joblib.load(self.paths.ranker_model)

    def build_request_context(self, user_id: str) -> dict[str, Any]:
        user = self.users[self.users["user_id"] == user_id].iloc[0]
        history = self.interactions[self.interactions["user_id"] == user_id].sort_values("shown_at")
        recent = history.tail(8)
        pool_counts = recent["pool_type"].value_counts().to_dict()
        return {
            "user_id": user_id,
            "user_profile": user.to_dict(),
            "interest_weights": parse_weight_map(user.get("interest_weights")),
            "skill_weights": parse_weight_map(user.get("skill_weights")),
            "recently_viewed_cards": recent["card_id"].tolist(),
            "recently_liked_cards": recent[recent["like"] == 1]["card_id"].tolist(),
            "recently_shared_cards": recent[recent["share"] == 1]["card_id"].tolist(),
            "recently_opened_detail_pages": recent[recent["open"] == 1]["card_id"].tolist(),
            "skipped_cards": recent[recent["skip_fast"] == 1]["card_id"].tolist(),
            "dwell_time_mean": float(recent["dwell_time_seconds"].mean()) if not recent.empty else 0.0,
            "per_pool_engagement": pool_counts,
            "session_depth": int(history["session_depth"].iloc[-1]) if not history.empty else 0,
            "cards_shown_in_session": len(recent),
            "recent_interaction_streak": int(recent["open"].sum() + recent["like"].sum()),
            "time_since_last_action_hours": self._time_since_last_action_hours(history),
            "exploration_budget": self.settings["retrieval"]["exploration_fraction"],
            "diversity_quota_status": 1.0 - max(pool_counts.values(), default=0) / max(1, len(recent)),
            "recent_pool_repetition": pool_counts,
            "novelty_counter": int(len(set(recent["card_id"]))),
        }

    def retrieve_candidates(self, context: dict[str, Any]) -> pd.DataFrame:
        user_id = context["user_id"]
        user = self.users[self.users["user_id"] == user_id].iloc[0]
        user_embedding = build_user_embedding(user, self.interactions, self.cards)
        embedding_dim = len(user_embedding) or default_dim_from_cards(self.cards)
        interest_weights = parse_weight_map(user.get("interest_weights"))
        skill_weights = parse_weight_map(user.get("skill_weights"))
        self.cards["retrieval_similarity"] = self.cards["embedding_vector"].apply(
            lambda raw: float(np.dot(user_embedding, np.array(parse_embedding(raw, default_dim=embedding_dim))))
        )

        recent_card_ids = set(context["recently_viewed_cards"])
        user_topics = set(split_pipe(user["interests"]))
        user_skills = set(split_pipe(user["skills"]))
        frames = []
        top_k = self.settings["retrieval"]["top_k_per_source"]
        for pool in CARD_TYPES:
            pool_cards = self.cards[self.cards["card_type"] == pool].copy()
            pool_cards["retrieval_reason"] = ""
            pool_cards["retrieval_strategy"] = ""
            pool_cards["weighted_onboarding_score"] = pool_cards.apply(
                lambda row: self._weighted_profile_score(row, interest_weights, skill_weights),
                axis=1,
            )

            onboarding = pool_cards[
                pool_cards["weighted_onboarding_score"] > 0.0
            ].nlargest(top_k, "weighted_onboarding_score")
            onboarding["retrieval_strategy"] = "onboarding_similarity"
            onboarding["retrieval_reason"] = "topic_or_skill_match"

            liked_cards = self.interactions[
                (self.interactions["user_id"] == user_id) & ((self.interactions["like"] == 1) | (self.interactions["open"] == 1))
            ]["card_id"].tolist()
            behavioral_interest_weights, behavioral_skill_weights = self._build_behavioral_weight_maps(liked_cards)
            if not behavioral_interest_weights:
                behavioral_interest_weights = {topic: interest_weights.get(topic, 1.0) for topic in user_topics}
            if not behavioral_skill_weights:
                behavioral_skill_weights = {skill: skill_weights.get(skill, 1.0) for skill in user_skills}
            pool_cards["behavioral_score"] = pool_cards.apply(
                lambda row: self._weighted_profile_score(row, behavioral_interest_weights, behavioral_skill_weights),
                axis=1,
            )
            behavioral = pool_cards[
                pool_cards["behavioral_score"] > 0.0
            ].nlargest(top_k, "behavioral_score")
            behavioral["retrieval_strategy"] = "behavioral_similarity"
            behavioral["retrieval_reason"] = "similar_to_engaged_cards"

            embedding = pool_cards.nlargest(top_k, "retrieval_similarity").copy()
            embedding["retrieval_strategy"] = "embedding_retrieval"
            embedding["retrieval_reason"] = "nearest_embedding"

            explore_count = max(1, int(top_k * self.settings["retrieval"]["exploration_fraction"]))
            exploration = pool_cards.sort_values("popularity_score").tail(explore_count).copy()
            exploration["retrieval_strategy"] = "exploration"
            exploration["retrieval_reason"] = "underexposed_novelty"

            trending = pool_cards[pool_cards["quality_score"] >= self.settings["retrieval"]["min_trending_quality"]].nlargest(
                top_k, "popularity_score"
            )
            trending["retrieval_strategy"] = "trending"
            trending["retrieval_reason"] = "platform_quality_signal"

            frames.extend([onboarding, behavioral, embedding, exploration, trending])

        candidates = pd.concat(frames, ignore_index=True)
        candidates = candidates.drop_duplicates(subset=["card_id"]).copy()
        candidates["lightweight_eligible"] = ~candidates["card_id"].isin(recent_card_ids)
        return candidates

    def hydrate_candidates(self, user_id: str, candidates: pd.DataFrame) -> pd.DataFrame:
        user = self.users[self.users["user_id"] == user_id].iloc[0]
        history = self.interactions[self.interactions["user_id"] == user_id]
        behavior = build_user_behavior_features(user_id, history)
        rows = []
        recently_liked = set(history[history["like"] == 1]["card_id"])
        recently_skipped = set(history[history["skip_fast"] == 1]["card_id"])
        liked_types = set(self.cards[self.cards["card_id"].isin(recently_liked)]["card_type"].tolist())
        skipped_types = set(self.cards[self.cards["card_id"].isin(recently_skipped)]["card_type"].tolist())
        user_embedding = build_user_embedding(user, history, self.cards)
        embedding_dim = len(user_embedding) or default_dim_from_cards(self.cards)
        for _, card in candidates.iterrows():
            card_dict = card.to_dict()
            overlap = compute_overlap_features(user, card)
            card_embedding = np.array(parse_embedding(card["embedding_vector"], default_dim=embedding_dim))
            card_dict.update(overlap)
            card_dict.update(behavior)
            card_dict["novelty_score"] = 1.0 if card["card_id"] not in set(history["card_id"]) else 0.2
            card_dict["diversity_contribution"] = 1.0 if card["card_type"] not in liked_types else 0.45
            card_dict["similarity_to_recent_likes"] = 0.8 if card["card_type"] in liked_types else 0.35
            card_dict["similarity_to_recent_skips"] = 0.8 if card["card_type"] in skipped_types else 0.2
            card_dict["mismatch_penalties"] = float(
                (1.0 - overlap["language_match"]) * 0.25 + (1.0 - overlap["format_match"]) * 0.15
            )
            card_dict["user_skill_vs_card_difficulty"] = overlap["difficulty_match"]
            card_dict["user_interest_vs_card_topic_density"] = overlap["topic_overlap_score"]
            card_dict["activity_vs_time_commitment"] = max(
                0.0, 1.0 - float(card["estimated_duration"]) / max(1.0, behavior["session_depth_mean"] * 12.0 + 7.0)
            )
            card_dict["format_preference_alignment"] = overlap["format_match"]
            card_dict["embedding_alignment"] = float(np.dot(user_embedding, card_embedding))
            for idx, value in enumerate(user_embedding):
                card_dict[f"user_emb_{idx}"] = float(value)
            for idx, value in enumerate(card_embedding):
                card_dict[f"card_emb_{idx}"] = float(value)
            rows.append(card_dict)
        return pd.DataFrame(rows)

    def apply_filters(self, user_id: str, hydrated: pd.DataFrame) -> pd.DataFrame:
        user = self.users[self.users["user_id"] == user_id].iloc[0]
        today = date.today().isoformat()
        filtered = hydrated.copy()
        filtered = filtered[filtered["application_deadline"] >= today]
        filtered = filtered[filtered["end_date"] >= today]
        filtered = filtered[(filtered["language"] == user["preferred_language"]) | (filtered["card_type"] == "news")]
        filtered = filtered[(filtered["location"] == user["region"]) | (filtered["format"] == "online") | (filtered["format"] == "hybrid")]
        filtered = filtered[filtered["status"] == "active"]
        filtered = filtered[filtered["integrity_score"] >= 0.7]
        filtered = filtered[filtered["lightweight_eligible"]]
        filtered["soft_filter_penalty"] = 0.0
        recent = self.interactions[self.interactions["user_id"] == user_id].tail(10)
        repeated_pools = recent["pool_type"].value_counts()
        repeated_orgs = self.cards[self.cards["card_id"].isin(recent["card_id"])]["host_organization"].value_counts()
        for idx, row in filtered.iterrows():
            penalty = 0.0
            penalty += 0.12 if repeated_pools.get(row["card_type"], 0) >= 3 else 0.0
            penalty += 0.1 if repeated_orgs.get(row["host_organization"], 0) >= 2 else 0.0
            penalty += 0.08 if float(row["quality_score"]) < 0.6 else 0.0
            penalty += 0.08 if float(row["novelty_score"]) < 0.5 else 0.0
            filtered.at[idx, "soft_filter_penalty"] = penalty
        return filtered

    def score_candidates(self, filtered: pd.DataFrame) -> pd.DataFrame:
        if filtered.empty:
            return filtered
        feature_frame = self._build_ranker_feature_frame(filtered)
        score_frame = filtered.copy()
        for target, model in self.ranker["models"].items():
            probabilities = model.predict_proba(feature_frame)
            score_frame[f"p_{target}"] = probabilities[:, 1] if probabilities.shape[1] > 1 else 0.0

        weights = self.settings["ranking"]["final_score_weights"]
        freshness_boost = score_frame["freshness_timestamp"].apply(self._freshness_boost)
        diversity_boost = score_frame["diversity_contribution"]
        quality_boost = score_frame["quality_score"]
        score_frame["final_score"] = (
            weights["open"] * score_frame["p_open"]
            + weights["like"] * score_frame["p_like"]
            + weights["share"] * score_frame["p_share"]
            + weights["long_view"] * score_frame["p_long_view"]
            - weights["skip_fast"] * score_frame["p_skip_fast"]
            - weights["disengage"] * score_frame["p_disengage"]
            + weights["freshness_boost"] * freshness_boost
            + weights["diversity_boost"] * diversity_boost
            + weights["quality_boost"] * quality_boost
            - score_frame["soft_filter_penalty"]
        )
        return score_frame.sort_values("final_score", ascending=False)

    def assemble_feed(self, scored: pd.DataFrame) -> pd.DataFrame:
        if scored.empty:
            return scored
        feed_size = self.settings["ranking"]["feed_size"]
        pool_limit = self.settings["ranking"]["max_cards_per_pool_in_feed"]
        selected = []
        pool_counter: dict[str, int] = {}
        topic_counter: dict[str, int] = {}
        organizer_counter: dict[str, int] = {}

        for _, row in scored.iterrows():
            if len(selected) >= feed_size:
                break
            pool = row["card_type"]
            if pool_counter.get(pool, 0) >= pool_limit:
                continue
            topics = split_pipe(row["topics"])
            organizer = row["host_organization"]
            adjusted_score = row["final_score"]
            if any(topic_counter.get(topic, 0) >= 2 for topic in topics):
                adjusted_score -= self.settings["ranking"]["topic_repeat_penalty"]
            if organizer_counter.get(organizer, 0) >= 1:
                adjusted_score -= self.settings["ranking"]["organizer_repeat_penalty"]
            row = row.copy()
            row["adjusted_final_score"] = adjusted_score
            selected.append(row)
            pool_counter[pool] = pool_counter.get(pool, 0) + 1
            organizer_counter[organizer] = organizer_counter.get(organizer, 0) + 1
            for topic in topics:
                topic_counter[topic] = topic_counter.get(topic, 0) + 1
        if not selected:
            return pd.DataFrame(columns=list(scored.columns) + ["adjusted_final_score"])
        return pd.DataFrame(selected).sort_values("adjusted_final_score", ascending=False).reset_index(drop=True)

    def update_feedback(self, user_id: str, card_id: str, action: str) -> None:
        timestamp = datetime.utcnow().isoformat()
        card = self.cards[self.cards["card_id"] == card_id].iloc[0]
        record = {
            "user_id": user_id,
            "card_id": card_id,
            "session_id": f"{user_id}_live",
            "session_depth": int(self.interactions[self.interactions["user_id"] == user_id]["session_depth"].max() or 0) + 1,
            "shown_at": timestamp,
            "pool_type": card["card_type"],
            "topic_overlap": 0,
            "skill_overlap": 0,
            "open": int(action == "open"),
            "like": int(action == "like"),
            "share": int(action == "share"),
            "long_view": int(action == "long_view"),
            "skip_fast": int(action == "skip_fast"),
            "disengage": int(action == "disengage"),
            "dwell_time_seconds": 45 if action == "long_view" else 5,
        }
        self.interactions = pd.concat([self.interactions, pd.DataFrame([record])], ignore_index=True)
        self.interactions.to_csv(self.paths.interactions_raw, index=False)
        self._update_profile_weights(user_id, card, action)

    def recommend(self, user_id: str) -> pd.DataFrame:
        context = self.build_request_context(user_id)
        candidates = self.retrieve_candidates(context)
        hydrated = self.hydrate_candidates(user_id, candidates)
        filtered = self.apply_filters(user_id, hydrated)
        scored = self.score_candidates(filtered)
        return self.assemble_feed(scored)

    def _build_ranker_feature_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        data = frame.copy()
        embedding_feature_columns = [
            column
            for column in self.ranker["feature_columns"]
            if column.startswith("user_emb_") or column.startswith("card_emb_")
        ]
        feature_columns = [
            "quality_score",
            "popularity_score",
            "editorial_priority",
            "integrity_score",
            "estimated_duration",
            "team_based",
            "retrieval_similarity",
            "topic_overlap_score",
            "skill_overlap_score",
            "skill_gain_score",
            "interest_weight_mean",
            "skill_weight_mean",
            "interest_match_count",
            "skill_match_count",
            "format_match",
            "language_match",
            "region_match",
            "difficulty_match",
            "opportunity_readiness_score",
            "recent_open_rate",
            "recent_like_rate",
            "recent_share_rate",
            "recent_skip_rate",
            "pool_entropy",
            "session_depth_mean",
        ] + embedding_feature_columns
        feature_frame = data[feature_columns].fillna(0.0)
        feature_frame = feature_frame.reindex(columns=self.ranker["feature_columns"], fill_value=0.0)
        return feature_frame

    def get_user_profile_snapshot(self, user_id: str, top_n: int = 5) -> dict[str, list[tuple[str, float]]]:
        user = self.users[self.users["user_id"] == user_id].iloc[0]
        interest_weights = parse_weight_map(user.get("interest_weights"))
        skill_weights = parse_weight_map(user.get("skill_weights"))
        return {
            "interests": sorted(interest_weights.items(), key=lambda item: item[1], reverse=True)[:top_n],
            "skills": sorted(skill_weights.items(), key=lambda item: item[1], reverse=True)[:top_n],
        }

    def _weighted_profile_score(
        self,
        card_row: pd.Series,
        interest_weights: dict[str, float],
        skill_weights: dict[str, float],
    ) -> float:
        personalization = self.settings["personalization"]
        topic_score = weighted_tag_match(interest_weights, set(split_pipe(card_row["topics"])))
        skill_score = weighted_tag_match(skill_weights, set(split_pipe(card_row["skills_required"])))
        return (
            personalization["interest_feature_weight"] * topic_score
            + personalization["skill_feature_weight"] * skill_score
        )

    def _build_behavioral_weight_maps(self, card_ids: list[str]) -> tuple[dict[str, float], dict[str, float]]:
        cards = self.cards[self.cards["card_id"].isin(card_ids)]
        interest_weights: dict[str, float] = {}
        skill_weights: dict[str, float] = {}
        for _, row in cards.iterrows():
            for topic in split_pipe(row["topics"]):
                interest_weights[topic] = interest_weights.get(topic, 0.0) + 1.0
            for skill in split_pipe(row["skills_required"]):
                skill_weights[skill] = skill_weights.get(skill, 0.0) + 1.2
            for skill in split_pipe(row["skills_gained"]):
                skill_weights[skill] = skill_weights.get(skill, 0.0) + 0.7
        return interest_weights, skill_weights

    def _update_profile_weights(self, user_id: str, card: pd.Series, action: str) -> None:
        user_index = self.users.index[self.users["user_id"] == user_id][0]
        user = self.users.loc[user_index].copy()
        interest_weights = parse_weight_map(user.get("interest_weights"))
        skill_weights = parse_weight_map(user.get("skill_weights"))
        personalization = self.settings["personalization"]
        base_delta = float(personalization["reaction_weight_updates"].get(action, 0.0))
        min_weight = float(personalization["min_profile_weight"])
        max_weight = float(personalization["max_profile_weight"])

        for topic in split_pipe(card["topics"]):
            start_weight = interest_weights.get(topic, float(personalization["cold_start_interest_weight"]))
            updated = np.clip(start_weight + base_delta * 0.85, min_weight, max_weight)
            if updated > min_weight or topic in interest_weights or base_delta > 0:
                interest_weights[topic] = round(float(updated), 4)

        for skill in split_pipe(card["skills_required"]):
            start_weight = skill_weights.get(skill, float(personalization["cold_start_skill_weight"]))
            updated = np.clip(start_weight + base_delta * 1.25, min_weight, max_weight)
            if updated > min_weight or skill in skill_weights or base_delta > 0:
                skill_weights[skill] = round(float(updated), 4)

        for skill in split_pipe(card["skills_gained"]):
            start_weight = skill_weights.get(skill, float(personalization["cold_start_skill_weight"]))
            updated = np.clip(start_weight + base_delta * 0.7, min_weight, max_weight)
            if updated > min_weight or skill in skill_weights or base_delta > 0:
                skill_weights[skill] = round(float(updated), 4)

        self.users.at[user_index, "interests"] = "|".join(sorted(interest_weights))
        self.users.at[user_index, "skills"] = "|".join(sorted(skill_weights))
        self.users.at[user_index, "interest_weights"] = self._serialize_weight_map(interest_weights)
        self.users.at[user_index, "skill_weights"] = self._serialize_weight_map(skill_weights)
        self.users.to_csv(self.paths.users_raw, index=False)

    @staticmethod
    def _serialize_weight_map(weight_map: dict[str, float]) -> str:
        return pd.Series(weight_map).sort_index().round(4).to_json()

    @staticmethod
    def _time_since_last_action_hours(history: pd.DataFrame) -> float:
        if history.empty:
            return 999.0
        last_ts = pd.to_datetime(history["shown_at"].iloc[-1])
        delta = datetime.utcnow() - last_ts.to_pydatetime()
        return round(delta.total_seconds() / 3600.0, 3)

    @staticmethod
    def _freshness_boost(timestamp: str) -> float:
        delta_days = (datetime.utcnow() - pd.to_datetime(timestamp).to_pydatetime()).days
        return max(0.0, 1.0 - delta_days / 30.0)
