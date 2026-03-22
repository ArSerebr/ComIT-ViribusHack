from fastapi import APIRouter, Query
from state.state_manager import get_state

router = APIRouter()


@router.get("/api/status")
def status(uid: str = Query(...)):
    state = get_state(uid)
    
    status = state.get("status")

    if not status:
        return {
            "model": "Multi-Agent",
            "status": "Ожидание",
            "statusColor": "#3CF0F0",
            "progress": 0
        }

    return {
        "model": status.get("agent", "AI"),
        "status": status.get("text", ""),
        "statusColor": status.get("color", "#4caf50"),
        "progress": status.get("progress", 0)
    }
