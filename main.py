from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from routes import tasks, status, tokens, history
from routes import Comit_chat

app = FastAPI()


@app.get("/")
def ui():
    return FileResponse("static/index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status.router)
app.include_router(tokens.router)
app.include_router(tasks.router)
app.include_router(history.router)
app.include_router(Comit_chat.router)
