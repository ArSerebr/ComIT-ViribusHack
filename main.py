from fastapi import FastAPI
from routes import tasks, chat, status, tokens, history

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для dev, потом сузим
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(status.router)
app.include_router(tokens.router)
app.include_router(tasks.router)
app.include_router(history.router)
