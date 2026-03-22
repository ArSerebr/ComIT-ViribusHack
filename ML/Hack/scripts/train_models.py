from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from student_recsys.training import train_models


if __name__ == "__main__":
    root = ROOT
    artifacts = train_models(root)
    print(
        "Trained models:",
        {
            "retrieval_users": len(artifacts.retrieval["user_embeddings"]),
            "retrieval_cards": len(artifacts.retrieval["card_embeddings"]),
            "rank_targets": artifacts.ranker["targets"],
        },
    )
