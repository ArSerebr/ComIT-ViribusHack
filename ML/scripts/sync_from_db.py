"""
Sync news_mini and news_featured from PostgreSQL to ML/News/data/raw/news.csv.

Usage:
  DATABASE_URL=postgresql://user:pass@host:5432/db python -m scripts.sync_from_db
  # or from ML/ dir: python scripts/sync_from_db.py

Requires: psycopg2 (pip install psycopg2-binary)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow run from ML/ or repo root
ML_ROOT = Path(__file__).resolve().parent.parent
if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

NEWS_CSV = ML_ROOT / "News" / "data" / "raw" / "news.csv"
EMBED_DIM = 12
DEFAULT_TOPICS = "product|design"
DEFAULT_SKILLS = "critical_thinking|data_literacy"


def _deterministic_embedding(text: str, dim: int = EMBED_DIM) -> str:
    """Generate deterministic 12-dim embedding from text (no API)."""
    values = []
    for idx in range(dim):
        digest = hashlib.sha256(f"{idx}::{text}".encode("utf-8")).digest()
        integer = int.from_bytes(digest[:8], "big", signed=False)
        values.append((integer / (2**64 - 1)) * 2 - 1)
    norm = sum(v * v for v in values) ** 0.5
    if norm == 0:
        norm = 1.0
    normalized = [round(v / norm, 4) for v in values]
    return str(normalized)


def _db_url_for_psycopg2(url: str) -> str:
    """Convert postgresql+asyncpg:// to postgresql:// for psycopg2."""
    if not url:
        return url
    for prefix in ("postgresql+asyncpg://", "postgresql+psycopg://"):
        if url.startswith(prefix):
            return "postgresql://" + url[len(prefix) :]
    return url


def fetch_news_from_db(database_url: str) -> tuple[list[dict], list[dict]]:
    """Fetch news_mini and news_featured from PostgreSQL."""
    try:
        import psycopg2
    except ImportError as e:
        raise SystemExit(
            "psycopg2 required. Install: pip install psycopg2-binary"
        ) from e

    conn_url = _db_url_for_psycopg2(database_url)
    conn = psycopg2.connect(conn_url)
    conn.autocommit = True
    cur = conn.cursor()

    mini_rows = []
    cur.execute(
        "SELECT id, title, image_url, details_url, sort_order FROM news_mini ORDER BY sort_order, id"
    )
    for row in cur.fetchall():
        mini_rows.append({
            "id": row[0],
            "title": row[1],
            "image_url": row[2],
            "details_url": row[3],
            "sort_order": row[4],
        })

    featured_rows = []
    cur.execute(
        """SELECT id, title, subtitle, description, image_url, cta_label, details_url, sort_order
           FROM news_featured ORDER BY sort_order, id"""
    )
    for row in cur.fetchall():
        featured_rows.append({
            "id": row[0],
            "title": row[1],
            "subtitle": row[2],
            "description": row[3],
            "image_url": row[4],
            "cta_label": row[5],
            "details_url": row[6],
            "sort_order": row[7],
        })

    cur.close()
    conn.close()
    return mini_rows, featured_rows


def row_to_news_csv(r: dict, card_type: str) -> dict:
    """Convert DB row to news.csv schema. card_id = DB id for backend mapping."""
    text_for_embed = f"{r['title']}"
    if card_type == "event":
        text_for_embed += " " + r.get("subtitle", "") + " " + r.get("description", "")
    embed = _deterministic_embedding(text_for_embed)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")

    return {
        "card_id": str(r["id"]),
        "card_type": card_type,
        "title": r["title"],
        "short_description": r.get("subtitle", r["title"][:200]),
        "full_description": r.get("description", r["title"]),
        "topics": DEFAULT_TOPICS,
        "skills_required": DEFAULT_SKILLS,
        "skills_gained": "",
        "news_category": "student_opportunity" if card_type == "event" else "policy_watch",
        "format": "online",
        "language": "en",
        "location": "EU",
        "published_at": now,
        "updated_at": now,
        "freshness_timestamp": now,
        "source_name": "ComIT",
        "source_type": "student_media",
        "author_name": "ComIT",
        "estimated_read_time_minutes": "3",
        "quality_score": "0.8",
        "popularity_score": "0.6",
        "editorial_priority": "0.7",
        "source_authority": "0.85",
        "topic_urgency": "0.5",
        "actionability_relevance": "0.7",
        "recency_score": "0.9",
        "breaking_score": "0.3",
        "novelty_score": "0.7",
        "integrity_score": "0.95",
        "status": "active",
        "embedding_vector": embed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync news_mini/featured from PostgreSQL to ML news.csv")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", ""),
        help="PostgreSQL URL (default: DATABASE_URL env)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print rows without writing",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge with existing news.csv, keep rows not from DB",
    )
    args = parser.parse_args()

    if not args.database_url:
        parser.error("DATABASE_URL or --database-url required")

    mini_rows, featured_rows = fetch_news_from_db(args.database_url)

    # Build CSV rows
    csv_rows = []
    seen_ids: set[str] = set()
    for r in mini_rows:
        row = row_to_news_csv(r, "news")
        if row["card_id"] not in seen_ids:
            seen_ids.add(row["card_id"])
            csv_rows.append(row)
    for r in featured_rows:
        row = row_to_news_csv(r, "event")
        if row["card_id"] not in seen_ids:
            seen_ids.add(row["card_id"])
            csv_rows.append(row)

    if args.merge and NEWS_CSV.exists():
        existing = []
        with NEWS_CSV.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            for r in reader:
                cid = r.get("card_id", "")
                if cid and cid not in seen_ids:
                    existing.append(r)
                    seen_ids.add(cid)
        csv_rows = csv_rows + existing

    if not csv_rows:
        print("No rows to write")
        return 0

    fieldnames = list(csv_rows[0].keys())
    if args.dry_run:
        print(f"Would write {len(csv_rows)} rows to {NEWS_CSV}")
        for r in csv_rows[:5]:
            print(f"  {r['card_id']} | {r['card_type']} | {r['title'][:50]}...")
        if len(csv_rows) > 5:
            print(f"  ... and {len(csv_rows) - 5} more")
        return 0

    NEWS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with NEWS_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Wrote {len(csv_rows)} rows to {NEWS_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
