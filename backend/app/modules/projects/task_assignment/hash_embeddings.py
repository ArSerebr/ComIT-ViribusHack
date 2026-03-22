"""Детерминированные эмбеддинги без внешнего API (dev / fallback)."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Iterable, List

_TOKEN_RE = re.compile(r"[\w\u0400-\u04FF]+", re.UNICODE)


class HashEmbeddingProvider:
    """Простой мешок хешей фиксированной размерности, L2-нормировка."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> List[float]:
        v = [0.0] * self.dim
        lower = (text or "").lower()
        for w in _TOKEN_RE.findall(lower):
            h = int(hashlib.sha256(w.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            v[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norm for x in v]
