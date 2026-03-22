from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from student_recsys.data_generation import generate_and_save


if __name__ == "__main__":
    root = ROOT
    bundle = generate_and_save(root)
    print(
        f"Generated datasets: users={len(bundle.users)}, cards={len(bundle.cards)}, interactions={len(bundle.interactions)}"
    )
