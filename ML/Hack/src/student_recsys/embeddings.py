from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from os import getenv
from typing import Any, Sequence

import numpy as np
import pandas as pd
import requests
import urllib3

from .features import parse_weight_map, split_pipe


DEFAULT_LOCAL_DIMENSION = 12
MIN_TRUNCATED_TEXT_CHARS = 256
DEFAULT_MAX_CARD_TEXT_CHARS = 1200
DEFAULT_MAX_USER_TEXT_CHARS = 1500


def get_embedding_service(settings: dict[str, Any]) -> "EmbeddingService":
    config = settings.get("embeddings", {})
    return _build_embedding_service(json.dumps(config, sort_keys=True))


@lru_cache(maxsize=4)
def _build_embedding_service(config_json: str) -> "EmbeddingService":
    config = json.loads(config_json)
    provider = str(config.get("provider", "gigachat")).lower()
    if provider == "gigachat":
        return GigaChatEmbeddingService(config=config)
    return LocalHashEmbeddingService(config=config)


@dataclass(slots=True)
class EmbeddingService:
    config: dict[str, Any]
    _cache: dict[str, list[float]] = field(default_factory=dict)

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        raise NotImplementedError


@dataclass(slots=True)
class LocalHashEmbeddingService(EmbeddingService):
    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        dimension = int(self.config.get("local_dimension", DEFAULT_LOCAL_DIMENSION))
        vectors: list[list[float]] = []
        for text in texts:
            cached = self._cache.get(text)
            if cached is not None:
                vectors.append(cached)
                continue
            values = np.zeros(dimension, dtype=float)
            for token in text.lower().split():
                values[abs(hash(token)) % dimension] += 1.0
            norm = np.linalg.norm(values) or 1.0
            vector = (values / norm).round(6).tolist()
            self._cache[text] = vector
            vectors.append(vector)
        return vectors


@dataclass(slots=True)
class GigaChatEmbeddingService(EmbeddingService):
    _access_token: str | None = None

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        self._disable_insecure_warning_if_needed()
        missing = [text for text in texts if text not in self._cache]
        if missing:
            self._populate_cache(missing)
        return [self._cache[text] for text in texts]

    def _populate_cache(self, texts: Sequence[str]) -> None:
        if not texts:
            return
        auth_key = self._resolve_auth_key()
        if not auth_key:
            fallback = LocalHashEmbeddingService(config=self.config)
            for text, vector in zip(texts, fallback.embed_texts(texts)):
                self._cache[text] = vector
            return

        batch_size = int(self.config.get("batch_size", 16))
        for start in range(0, len(texts), batch_size):
            batch = list(texts[start : start + batch_size])
            self._populate_batch(auth_key, batch)

    def _populate_batch(self, auth_key: str, texts: Sequence[str]) -> None:
        response = self._post_embeddings(auth_key, texts)
        if response.status_code == 413:
            if len(texts) > 1:
                midpoint = max(1, len(texts) // 2)
                self._populate_batch(auth_key, texts[:midpoint])
                self._populate_batch(auth_key, texts[midpoint:])
                return
            original = texts[0]
            truncated = self._truncate_text(original)
            if truncated == original:
                response.raise_for_status()
            self._populate_batch(auth_key, [truncated])
            self._cache[original] = self._cache[truncated]
            return
        response.raise_for_status()
        payload = response.json()
        items = sorted(payload.get("data", []), key=lambda item: item.get("index", 0))
        if len(items) != len(texts):
            raise ValueError("GigaChat returned an unexpected number of embeddings.")
        for text, item in zip(texts, items):
            self._cache[text] = [float(value) for value in item["embedding"]]

    def _post_embeddings(self, auth_key: str, texts: Sequence[str]) -> requests.Response:
        attempts = int(self.config.get("request_retries", 4))
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                response = requests.post(
                    self.config.get("api_url", "https://gigachat.devices.sberbank.ru/api/v1/embeddings"),
                    headers={
                        "Accept": "application/json",
                        "Authorization": f"Bearer {self._get_access_token(auth_key)}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.config.get("model", "Embeddings"),
                        "input": list(texts),
                    },
                    timeout=float(self.config.get("timeout_seconds", 60)),
                    verify=self._resolve_verify_setting(),
                )
                if response.status_code == 401:
                    self._access_token = None
                    response = requests.post(
                        self.config.get("api_url", "https://gigachat.devices.sberbank.ru/api/v1/embeddings"),
                        headers={
                            "Accept": "application/json",
                            "Authorization": f"Bearer {self._get_access_token(auth_key)}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.config.get("model", "Embeddings"),
                            "input": list(texts),
                        },
                        timeout=float(self.config.get("timeout_seconds", 60)),
                        verify=self._resolve_verify_setting(),
                    )
                return response
            except requests.RequestException as error:
                last_error = error
                if attempt == attempts - 1:
                    raise
                time.sleep(min(2**attempt, 8))
        if last_error is not None:
            raise last_error
        raise RuntimeError("Failed to request embeddings from GigaChat.")

    def _get_access_token(self, auth_key: str) -> str:
        if self._access_token:
            return self._access_token
        attempts = int(self.config.get("request_retries", 4))
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                response = requests.post(
                    self.config.get("auth_url", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"),
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json",
                        "RqUID": str(uuid.uuid4()),
                        "Authorization": f"Basic {auth_key}",
                    },
                    data={"scope": self.config.get("scope", "GIGACHAT_API_PERS")},
                    timeout=float(self.config.get("timeout_seconds", 60)),
                    verify=self._resolve_verify_setting(),
                )
                response.raise_for_status()
                payload = response.json()
                self._access_token = str(payload["access_token"])
                return self._access_token
            except requests.RequestException as error:
                last_error = error
                if attempt == attempts - 1:
                    raise
                time.sleep(min(2**attempt, 8))
        if last_error is not None:
            raise last_error
        raise RuntimeError("Failed to obtain GigaChat access token.")

    def _resolve_auth_key(self) -> str:
        env_name = str(self.config.get("auth_key_env", "GIGACHAT_AUTH_KEY"))
        return str(getenv(env_name, self.config.get("auth_key", ""))).strip()

    def _resolve_verify_setting(self) -> bool | str:
        ca_bundle = str(self.config.get("ca_bundle_path", "")).strip()
        if ca_bundle:
            return ca_bundle
        return bool(self.config.get("verify_ssl", True))

    def _disable_insecure_warning_if_needed(self) -> None:
        if not self._resolve_verify_setting():
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _truncate_text(self, text: str) -> str:
        compact = " ".join(text.split())
        if len(compact) <= MIN_TRUNCATED_TEXT_CHARS:
            return compact
        target_length = max(MIN_TRUNCATED_TEXT_CHARS, len(compact) // 2)
        return compact[:target_length]


def build_card_embedding_text(card: pd.Series | dict[str, Any]) -> str:
    source = card if isinstance(card, dict) else card.to_dict()
    text = "\n".join(
        [
            f"title: {source.get('title', '')}",
            f"type: {source.get('card_type', '')}",
            f"short_description: {source.get('short_description', '')}",
            f"topics: {', '.join(split_pipe(source.get('topics')))}",
            f"skills_required: {', '.join(split_pipe(source.get('skills_required')))}",
            f"skills_gained: {', '.join(split_pipe(source.get('skills_gained')))}",
            f"format: {source.get('format', '')}",
            f"language: {source.get('language', '')}",
            f"location: {source.get('location', '')}",
            f"organization: {source.get('host_organization', '')}",
        ]
    )
    return text[:DEFAULT_MAX_CARD_TEXT_CHARS]


def build_user_embedding_text(user_row: pd.Series, interactions: pd.DataFrame, cards: pd.DataFrame) -> str:
    user_id = user_row["user_id"] if "user_id" in user_row.index else str(user_row.name)
    interest_weights = parse_weight_map(user_row.get("interest_weights"))
    skill_weights = parse_weight_map(user_row.get("skill_weights"))
    weighted_interests = ", ".join(_top_weighted_tags(interest_weights, limit=6))
    weighted_skills = ", ".join(_top_weighted_tags(skill_weights, limit=8))

    history = interactions[interactions["user_id"] == user_id].sort_values("shown_at").tail(8)
    history_cards = cards[["card_id", "card_type", "topics", "skills_required", "skills_gained"]]
    lines = [
        f"user_id: {user_id}",
        f"experience_level: {user_row.get('experience_level', '')}",
        f"preferred_language: {user_row.get('preferred_language', '')}",
        f"region: {user_row.get('region', '')}",
        f"preferred_formats: {', '.join(split_pipe(user_row.get('preferred_formats')))}",
        f"weighted_interests: {weighted_interests}",
        f"weighted_skills: {weighted_skills}",
    ]
    if history.empty:
        lines.append("history: none")
        return "\n".join(lines)[:DEFAULT_MAX_USER_TEXT_CHARS]

    merged = history.merge(history_cards, on="card_id", how="left")
    positive_topics, negative_topics = _collect_history_signals(merged, "topics")
    positive_skills, negative_skills = _collect_history_signals(merged, "skills_required")
    gained_skills, _ = _collect_history_signals(merged, "skills_gained")
    recent_types = ", ".join(merged["card_type"].astype(str).tail(4).tolist())
    lines.extend(
        [
            f"recent_card_types: {recent_types}",
            f"positive_topics: {', '.join(_format_counter(positive_topics, limit=6))}",
            f"negative_topics: {', '.join(_format_counter(negative_topics, limit=4))}",
            f"positive_skills: {', '.join(_format_counter(positive_skills, limit=8))}",
            f"negative_skills: {', '.join(_format_counter(negative_skills, limit=5))}",
            f"gained_skills: {', '.join(_format_counter(gained_skills, limit=6))}",
        ]
    )
    return "\n".join(lines)[:DEFAULT_MAX_USER_TEXT_CHARS]


def _top_weighted_tags(weight_map: dict[str, float], limit: int) -> list[str]:
    return [f"{tag}:{weight:.3f}" for tag, weight in sorted(weight_map.items(), key=lambda item: item[1], reverse=True)[:limit]]


def _collect_history_signals(history: pd.DataFrame, field_name: str) -> tuple[dict[str, float], dict[str, float]]:
    positive: dict[str, float] = {}
    negative: dict[str, float] = {}
    for _, row in history.iterrows():
        positive_strength = (
            1.2 * int(row.get("like", 0))
            + 1.5 * int(row.get("share", 0))
            + 0.7 * int(row.get("open", 0))
            + 1.0 * int(row.get("long_view", 0))
        )
        negative_strength = 1.1 * int(row.get("skip_fast", 0)) + 1.4 * int(row.get("disengage", 0))
        for tag in split_pipe(row.get(field_name)):
            if positive_strength:
                positive[tag] = positive.get(tag, 0.0) + positive_strength
            if negative_strength:
                negative[tag] = negative.get(tag, 0.0) + negative_strength
    return positive, negative


def _format_counter(counter: dict[str, float], limit: int) -> list[str]:
    if not counter:
        return ["none"]
    return [f"{tag}:{weight:.2f}" for tag, weight in sorted(counter.items(), key=lambda item: item[1], reverse=True)[:limit]]
