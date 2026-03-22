"""
ML HTTP API for recommendations.

Endpoints:
- GET /recommend/news?user_id={uuid}&limit=10 — news recommendations
- GET /recommend/events?user_id={uuid}&limit=10 — event recommendations (card_type in [event, meetup, hackathon])
- POST /feedback — record interaction for real-time adaptation
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

# ML/News — sys.path must be set before recommender import
BASE_DIR = Path(__file__).resolve().parent
NEWS_DIR = BASE_DIR / "News"
sys.path.insert(0, str(NEWS_DIR))

from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from recommender import load_cards, load_users, recommend_top_news  # noqa: E402

app = FastAPI(
    title="ML Recommendation API",
    description="News and event recommendations for ComIT Viribus",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USERS_PATH = NEWS_DIR / "data" / "raw" / "students.csv"
CARDS_PATH = NEWS_DIR / "data" / "raw" / "news.csv"
INTERACTIONS_PATH = NEWS_DIR / "data" / "raw" / "interactions.csv"

EVENT_CARD_TYPES = frozenset({"event", "meetup", "hackathon"})


def _fallback_news(user_id: str, limit: int) -> list[dict]:
    """Cold-start: return top news by recency when user not in CSV."""
    cards = load_cards()
    news_cards = [c for c in cards if c.get("card_type") == "news" and c.get("status") == "active"]
    news_cards.sort(
        key=lambda c: (c.get("recency_score", 0), c.get("updated_at", "")),
        reverse=True,
    )
    result = []
    for card in news_cards[:limit]:
        result.append({
            "card_id": card["card_id"],
            "title": card["title"],
            "card_type": card.get("card_type", "news"),
            "topics": card.get("topics_list", []),
            "why": ["recency fallback (cold start)"],
            "final_score": 0.0,
        })
    return result


def _fallback_events(user_id: str, limit: int) -> list[dict]:
    """Cold-start: return top events by recency when user not in CSV."""
    cards = load_cards()
    event_cards = [
        c for c in cards
        if c.get("card_type") in EVENT_CARD_TYPES and c.get("status") == "active"
    ]
    event_cards.sort(
        key=lambda c: (c.get("recency_score", 0), c.get("updated_at", "")),
        reverse=True,
    )
    result = []
    for card in event_cards[:limit]:
        result.append({
            "card_id": card["card_id"],
            "title": card["title"],
            "card_type": card.get("card_type", "event"),
            "topics": card.get("topics_list", []),
            "why": ["recency fallback (cold start)"],
            "final_score": 0.0,
        })
    return result


def _filter_events(recommendations: list[dict]) -> list[dict]:
    """Filter recommendations to event card types."""
    return [r for r in recommendations if r.get("card_type") in EVENT_CARD_TYPES]


def _ensure_user_in_csv(user_id: str) -> None:
    """Ensure user exists in students.csv for feedback. Create minimal row if missing."""
    users = load_users()
    if user_id in users:
        return
    # Append minimal user row
    row = {
        "user_id": user_id,
        "interests": "",
        "skills": "",
        "interest_weights": "{}",
        "skill_weights": "{}",
        "experience_level": "junior",
        "preferred_language": "en",
        "region": "EU",
        "preferred_formats": "briefing|newsletter",
        "freshness_preference": "1.0",
        "breaking_affinity": "0.9",
        "source_loyalty_weights": "{}",
        "onboarding_completed_at": datetime.now(timezone.utc).isoformat(),
    }
    file_exists = USERS_PATH.exists()
    with USERS_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(row.keys()),
            lineterminator="\n",
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def _append_interaction(user_id: str, card_id: str, reaction: str) -> None:
    """Append interaction row to interactions.csv."""
    _ensure_user_in_csv(user_id)
    reaction_map = {
        "open": (1, 0, 0, 0, 0, 0, 30),
        "like": (0, 1, 0, 0, 0, 0, 25),
        "share": (0, 0, 1, 0, 0, 0, 35),
        "long_view": (0, 0, 0, 1, 0, 0, 60),
        "skip_fast": (0, 0, 0, 0, 1, 0, 3),
        "disengage": (0, 0, 0, 0, 0, 1, 5),
    }
    vals = reaction_map.get(reaction, (0, 0, 0, 0, 0, 0, 10))
    open_v, like_v, share_v, long_view_v, skip_fast_v, disengage_v, dwell = vals

    cards = load_cards()
    cards_by_id = {c["card_id"]: c for c in cards}
    card = cards_by_id.get(card_id, {})
    pool_type = card.get("card_type", "news")

    now = datetime.now(timezone.utc).isoformat()
    session_id = f"{user_id}_api_{now[:10]}"

    # Get next session_depth
    depth = 1
    if INTERACTIONS_PATH.exists():
        with INTERACTIONS_PATH.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("user_id") == user_id:
                    depth = max(depth, int(row.get("session_depth", 0)) + 1)

    new_row = {
        "user_id": user_id,
        "card_id": card_id,
        "session_id": session_id,
        "session_depth": str(depth),
        "shown_at": now,
        "pool_type": pool_type,
        "topic_overlap": "0",
        "skill_overlap": "0",
        "open": str(open_v),
        "like": str(like_v),
        "share": str(share_v),
        "long_view": str(long_view_v),
        "skip_fast": str(skip_fast_v),
        "disengage": str(disengage_v),
        "dwell_time_seconds": str(dwell),
    }

    file_exists = INTERACTIONS_PATH.exists()
    with INTERACTIONS_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(new_row.keys()), lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerow(new_row)


@app.get("/health")
def health() -> dict:
    """Health check."""
    return {"status": "ok", "service": "ml-api"}


def _add_card_types(recs: list[dict]) -> None:
    """Add card_type to each recommendation from cards lookup."""
    cards = load_cards()
    by_id = {c["card_id"]: c for c in cards}
    for r in recs:
        r["card_type"] = by_id.get(r["card_id"], {}).get("card_type", "news")


@app.get("/recommend/news")
def recommend_news(
    user_id: str = Query(..., description="User UUID"),
    limit: int = Query(10, ge=1, le=50, description="Max recommendations"),
) -> list[dict]:
    """
    Get personalized news recommendations.
    Cold-start: returns top by recency if user not in ML profile.
    """
    try:
        recs = recommend_top_news(str(user_id), limit)
        _add_card_types(recs)
        news_recs = [r for r in recs if r.get("card_type", "news") == "news"]
        return news_recs[:limit]
    except ValueError:
        # Unknown user_id — cold start
        return _fallback_news(str(user_id), limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/recommend/events")
def recommend_events(
    user_id: str = Query(..., description="User UUID"),
    limit: int = Query(10, ge=1, le=50, description="Max recommendations"),
) -> list[dict]:
    """
    Get event recommendations (card_type in [event, meetup, hackathon]).
    Cold-start: returns top by recency if user not in ML profile.
    """
    try:
        recs = recommend_top_news(str(user_id), limit * 3)  # Over-fetch then filter
        _add_card_types(recs)
        event_recs = _filter_events(recs)
        return event_recs[:limit]
    except ValueError:
        return _fallback_events(str(user_id), limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


class FeedbackBody(BaseModel):
    """Feedback payload for POST /feedback."""

    user_id: str = Field(..., description="User UUID")
    card_id: str = Field(..., description="Card identifier")
    reaction: str = Field(
        ...,
        description="Reaction: open, like, share, long_view, skip_fast, disengage",
    )


VALID_REACTIONS = frozenset({"open", "like", "share", "long_view", "skip_fast", "disengage"})


@app.post("/feedback")
def feedback(body: FeedbackBody) -> dict:
    """
    Record user reaction for real-time profile adaptation.
    Appends to interactions.csv; creates user in students.csv if cold start.
    """
    if body.reaction not in VALID_REACTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"reaction must be one of: {sorted(VALID_REACTIONS)}",
        )
    try:
        _append_interaction(body.user_id, body.card_id, body.reaction)
        return {"ok": True, "user_id": body.user_id, "card_id": body.card_id, "reaction": body.reaction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


