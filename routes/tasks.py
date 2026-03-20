from fastapi import APIRouter, HTTPException
from state.state_manager import get_task

router = APIRouter()

@router.get("/api/task/{task_id}")
def get_task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    response = {
        "task_id": task["task_id"],
        "status": task["status"]
    }
    
    if task["status"] == "READY":
        response["result"] = task["result"]
    
    return response
