from __future__ import annotations

import hashlib
import json
import os
import uuid
import warnings
from datetime import UTC, datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


BASE_DIR = Path(__file__).resolve().parent
CACHE_PATH = BASE_DIR / ".cache" / "gigachat_embeddings.json"
TARGET_DIM = 12

OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
MODELS_URL = "https://gigachat.devices.sberbank.ru/api/v1/models"
EMBEDDINGS_URL = "https://gigachat.devices.sberbank.ru/api/v1/embeddings"


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize_vector(vector: list[float]) -> list[float]:
    norm = sum(value * value for value in vector) ** 0.5
    if norm == 0:
        return [0.0] * len(vector)
    return [round(value / norm, 4) for value in vector]


def _deterministic_vector(text: str, target_dim: int = TARGET_DIM) -> list[float]:
    values = []
    for idx in range(target_dim):
        digest = hashlib.sha256(f"{idx}::{text}".encode("utf-8")).digest()
        integer = int.from_bytes(digest[:8], "big", signed=False)
        values.append((integer / (2**64 - 1)) * 2 - 1)
    return normalize_vector(values)


def _project_vector(vector: list[float], target_dim: int = TARGET_DIM) -> list[float]:
    if not vector:
        return [0.0] * target_dim
    if len(vector) == target_dim:
        return normalize_vector(vector)

    projected = []
    step = len(vector) / target_dim
    for idx in range(target_dim):
        start = int(round(idx * step))
        end = int(round((idx + 1) * step))
        if end <= start:
            end = min(start + 1, len(vector))
        segment = vector[start:end] or [vector[min(start, len(vector) - 1)]]
        projected.append(sum(segment) / len(segment))
    return normalize_vector(projected)


class GigaChatEmbeddingProvider:
    def __init__(self) -> None:
        self.auth_key = os.getenv("GIGACHAT_AUTH_KEY", "").strip()
        self.scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS").strip()
        self.model = os.getenv("GIGACHAT_EMBEDDING_MODEL", "Embeddings").strip()
        self.verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL", "true").lower() not in {"0", "false", "no"}
        self.timeout_seconds = int(os.getenv("GIGACHAT_TIMEOUT_SECONDS", "60"))
        self._token: str | None = None
        self._token_expires_at: datetime | None = None
        self._models_checked = False
        self.cache = self._load_cache()
        if not self.verify_ssl:
            warnings.filterwarnings("ignore", message="Unverified HTTPS request")

    def _load_cache(self) -> dict[str, list[float]]:
        if not CACHE_PATH.exists():
            return {}
        try:
            with CACHE_PATH.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            return {}
        return {}

    def _save_cache(self) -> None:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CACHE_PATH.open("w", encoding="utf-8") as handle:
            json.dump(self.cache, handle, ensure_ascii=True, separators=(",", ":"))

    def _cache_key(self, text: str) -> str:
        raw = f"{self.model}|{TARGET_DIM}|{text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _request_access_token(self) -> str | None:
        if not self.auth_key or requests is None:
            return None
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {self.auth_key}",
        }
        try:
            response = requests.post(
                OAUTH_URL,
                headers=headers,
                data={"scope": self.scope},
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return None
        self._token = payload.get("access_token")

        expires_at = payload.get("expires_at")
        if isinstance(expires_at, (int, float)):
            if expires_at > 10_000_000_000:
                self._token_expires_at = datetime.fromtimestamp(expires_at / 1000, UTC)
            else:
                self._token_expires_at = datetime.fromtimestamp(expires_at, UTC)
        else:
            self._token_expires_at = datetime.now(UTC) + timedelta(minutes=25)
        return self._token

    def get_access_token(self) -> str | None:
        if self._token and self._token_expires_at:
            if datetime.now(UTC) + timedelta(minutes=1) < self._token_expires_at:
                return self._token
        return self._request_access_token()

    def list_models(self) -> list[str]:
        token = self.get_access_token()
        if not token or requests is None:
            return []
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        try:
            response = requests.get(
                MODELS_URL,
                headers=headers,
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return []
        models = []
        for item in payload.get("data", []):
            model_id = item.get("id")
            if model_id:
                models.append(model_id)
        return models

    def _ensure_model_available(self) -> None:
        if self._models_checked:
            return
        self._models_checked = True
        available_models = self.list_models()
        if available_models and self.model not in available_models:
            raise ValueError(
                f"GigaChat embedding model `{self.model}` not available. Found: {', '.join(available_models)}"
            )

    def embed_text(self, text: str) -> list[float]:
        normalized_text = " ".join(text.split())
        cache_key = self._cache_key(normalized_text)
        if cache_key in self.cache:
            return self.cache[cache_key]

        vector = self._embed_via_api(normalized_text)
        self.cache[cache_key] = vector
        self._save_cache()
        return vector

    def _embed_via_api(self, text: str) -> list[float]:
        token = self.get_access_token()
        if not token or requests is None:
            return _deterministic_vector(text)

        self._ensure_model_available()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {
            "model": self.model,
            "input": [text],
        }
        try:
            response = requests.post(
                EMBEDDINGS_URL,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
            body = response.json()
        except Exception:
            return _deterministic_vector(text)
        raw_vectors = body.get("data", [])
        if not raw_vectors:
            return _deterministic_vector(text)
        full_vector = raw_vectors[0].get("embedding", [])
        if not full_vector:
            return _deterministic_vector(text)
        return _project_vector(full_vector, TARGET_DIM)

    def embed_weighted_tokens(self, weighted_tokens: list[tuple[str, float]]) -> list[float]:
        weighted_tokens = sorted(weighted_tokens, key=lambda item: item[0])
        lines = []
        for token, weight in weighted_tokens:
            token_name = token.replace("::", " ")
            lines.append(f"{token_name} weight {float(weight):.4f}")
        prompt = (
            "Create an embedding for personalized news recommendation.\n"
            "This text describes a weighted user profile or weighted news metadata.\n"
            + "\n".join(lines)
        )
        return self.embed_text(prompt)


_DEFAULT_PROVIDER: GigaChatEmbeddingProvider | None = None


def get_embedding_provider() -> GigaChatEmbeddingProvider:
    global _DEFAULT_PROVIDER
    if _DEFAULT_PROVIDER is None:
        _DEFAULT_PROVIDER = GigaChatEmbeddingProvider()
    return _DEFAULT_PROVIDER


def embed_weighted_tokens(weighted_tokens: list[tuple[str, float]]) -> list[float]:
    return get_embedding_provider().embed_weighted_tokens(weighted_tokens)
