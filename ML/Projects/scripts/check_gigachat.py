from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from student_recsys.data_generation import load_settings
from student_recsys.embeddings import GigaChatEmbeddingService, get_embedding_service


def main() -> None:
    settings = load_settings(ROOT)
    service = get_embedding_service(settings)
    if not isinstance(service, GigaChatEmbeddingService):
        raise RuntimeError("Configured embedding provider is not GigaChat.")

    auth_key = service._resolve_auth_key()
    if not auth_key:
        raise RuntimeError("GigaChat auth key is missing.")

    token = service._get_access_token(auth_key)
    models = service.list_models()
    vector = service.embed_text("student project recommendation test")

    print("GigaChat check")
    print(f"token_received: {bool(token)}")
    print(f"models_count: {len(models)}")
    print(f"embedding_dim: {len(vector)}")
    print("first_models:")
    print(json.dumps(models[:5], ensure_ascii=False, indent=2))
    print("embedding_preview:")
    print(json.dumps(vector[:10], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
