from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/api/tokens")
def tokens(uid: str = Query(...)):
    """
    Заглушка для фронта и будущего биллинга
    """
    return {
        "tokens": 15,
        "cost": 0
    }
