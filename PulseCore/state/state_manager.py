from db.mongo import states, tasks
from agents.agent_registry import AGENTS_METADATA
import uuid
from datetime import datetime


def get_state(uid: str) -> dict:
    return states.find_one({"uid": uid}) or {
        "uid": uid,
        "stage": "idle",
        "ideas": [],
        "selected_idea": None
    }


def save_state(uid: str, data: dict):
    states.update_one(
        {"uid": uid},
        {"$set": data},
        upsert=True
    )


def set_agent_status(uid: str, agent_name: str, progress: int):
    agent = AGENTS_METADATA.get(agent_name, {})

    states.update_one(
        {"uid": uid},
        {"$set": {
            "status": {
                "agent": agent_name,
                "text": agent.get("text", ""),
                "color": agent.get("color", "#9e9e9e"),
                "progress": progress
            }
        }},
        upsert=True
    )


def update_status(uid: str, agent: str, text: str, color: str, progress: int):
    states.update_one(
        {"uid": uid},
        {"$set": {
            "status": {
                "agent": agent,
                "text": text,
                "color": color,
                "progress": progress
            }
        }},
        upsert=True
    )

def create_task(uid: str) -> str:
    task_id = str(uuid.uuid4())
    tasks.insert_one({
        "task_id": task_id,
        "uid": uid,
        "status": "PENDING",
        "result": None,
        "created_at": datetime.utcnow().isoformat()
    })
    return task_id

def update_task(task_id: str, status: str, result: dict = None):
    update_data = {"status": status}
    if result is not None:
        update_data["result"] = result
    
    tasks.update_one(
        {"task_id": task_id},
        {"$set": update_data}
    )

def get_task(task_id: str) -> dict:
    return tasks.find_one({"task_id": task_id})
def log_event(uid: str, event: dict):
    states.update_one(
        {"uid": uid},
        {"$push": {
            "events": {
                **event,
                "ts": datetime.utcnow().isoformat()
            }
        }},
        upsert=True
    )

def save_message(uid: str, role: str, content: str, buttons: list = None):
    from db.mongo import messages
    messages.insert_one({
        "uid": uid,
        "role": role,
        "content": content,
        "buttons": buttons or [],
        "created_at": datetime.utcnow().isoformat()
    })

def get_messages(uid: str):
    from db.mongo import messages
    return list(messages.find({"uid": uid}).sort("created_at", 1))
