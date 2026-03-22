import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Iterable, List


class GigaChatEmbeddingsClient:
    def __init__(
        self,
        auth_key: str | None = None,
        scope: str = "GIGACHAT_API_PERS",
        model: str = "EmbeddingsGigaR",
        verify_ssl: bool | None = None,
    ):
        self.auth_key = auth_key or os.getenv("GIGACHAT_AUTH_KEY")
        self.scope = os.getenv("GIGACHAT_SCOPE", scope)
        self.model = os.getenv("GIGACHAT_EMBEDDING_MODEL", model)
        self.verify_ssl = self._parse_verify_ssl(verify_ssl)
        self.access_token = os.getenv("GIGACHAT_ACCESS_TOKEN")
        self.token_expires_at = 0.0

        if not self.auth_key and not self.access_token:
            raise RuntimeError(
                "Set `GIGACHAT_AUTH_KEY` or `GIGACHAT_ACCESS_TOKEN` before running the model."
            )

    @staticmethod
    def _parse_verify_ssl(verify_ssl: bool | None) -> bool:
        if verify_ssl is not None:
            return verify_ssl
        env_value = os.getenv("GIGACHAT_VERIFY_SSL", "false").strip().lower()
        return env_value in {"1", "true", "yes", "on"}

    def _ssl_context(self):
        if self.verify_ssl:
            return ssl.create_default_context()

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    def _request_json(self, method: str, url: str, headers: dict, payload: dict | None = None):
        data = None
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        request = urllib.request.Request(url=url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, context=self._ssl_context(), timeout=60) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GigaChat API request failed: {error.code} {body}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"GigaChat API connection error: {error}") from error

    def _ensure_access_token(self) -> str:
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        if self.access_token and self.token_expires_at == 0.0 and not self.auth_key:
            return self.access_token

        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        form_data = urllib.parse.urlencode({"scope": self.scope}).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {self.auth_key}",
        }
        request = urllib.request.Request(url=url, data=form_data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, context=self._ssl_context(), timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Failed to get Sber access token: {error.code} {body}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"Failed to connect to Sber token endpoint: {error}") from error

        token = payload.get("access_token")
        if not token:
            raise RuntimeError(f"Sber token response did not contain `access_token`: {payload}")

        expires_at = payload.get("expires_at")
        if isinstance(expires_at, (int, float)) and expires_at > 10_000_000_000:
            expires_at = float(expires_at) / 1000.0
        if isinstance(expires_at, (int, float)) and expires_at > time.time():
            self.token_expires_at = float(expires_at) - 60
        else:
            self.token_expires_at = time.time() + 29 * 60

        self.access_token = token
        return token

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        inputs = list(texts)
        if not inputs:
            return []

        payload = {
            "model": self.model,
            "input": inputs,
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._ensure_access_token()}",
        }
        response = self._request_json(
            method="POST",
            url="https://gigachat.devices.sberbank.ru/api/v1/embeddings",
            headers=headers,
            payload=payload,
        )

        data = sorted(response.get("data", []), key=lambda item: item["index"])
        embeddings = [self._normalize(item["embedding"]) for item in data]
        if len(embeddings) != len(inputs):
            raise RuntimeError(
                f"Expected {len(inputs)} embeddings from Sber, got {len(embeddings)}. Response: {response}"
            )
        return embeddings

    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        norm = sum(value * value for value in vector) ** 0.5 or 1.0
        return [value / norm for value in vector]
