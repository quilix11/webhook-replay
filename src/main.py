from fastapi import FastAPI
from src.api.webhooks import router as webhooks_router

app = FastAPI(
    title="Webhook Replay Server",
    version="1.0.0"
)

app.include_router(webhooks_router)