from fastapi import APIRouter, Query
from state.state_manager import get_messages

router = APIRouter()

@router.get("/api/history/{uid}")
def history(uid: str):
    messages = get_messages(uid)
    # Форматируем для фронта, убираем _id из монго
    return [
        {
            "role": m["role"],
            "content": m["content"],
            "buttons": m.get("buttons", []),
            "created_at": m.get("created_at")
        }
        for m in messages
    ]
