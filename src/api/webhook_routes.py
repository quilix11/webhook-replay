from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database_session import get_async_session
from src.services.webhook_operations import save_webhook, get_all_webhooks, replay_webhooks
from src.models.webhook_entity import WebHook
from sqlalchemy import select
import httpx

router = APIRouter()

async def intercept_data(request: Request):
    headers = dict(request.headers)
    try:
        data = await request.json()
    except Exception:
        body_bytes = await request.body()
        data = {"raw_data": body_bytes.decode(errors="ignore")}
    return{"headers": headers, "body": data}

@router.post("/webhooks/receive")
async def receive(payload: dict = Depends(intercept_data), session: AsyncSession = Depends(get_async_session)):
    saved_webhook = await save_webhook(session, payload["headers"], payload["body"])
    return {"status": "success", "id": saved_webhook.id}

@router.get("/webhooks/list")
async def list_webhooks(session: AsyncSession = Depends(get_async_session)):
    webhooks = await get_all_webhooks(session)
    return {"status": "success", "count": len(webhooks), "data": webhooks}

@router.get("/webhooks/{id}")
async def get_hook(id: int, session: AsyncSession = Depends(get_async_session)):
    db_hook = await session.execute(select(WebHook).where(WebHook.id == id))
    hook = db_hook.scalar_one_or_none()
    if hook is None:
        raise HTTPException(status_code=404, detail="WebHook not found")
    return hook

@router.post("/webhooks/{id}/replay")
async def replay_hook(id:int, target:str, session: AsyncSession = Depends(get_async_session)):
    replay = await replay_webhooks(session= session, webhook_id= id, target_url= target)
    if replay is None:
        raise HTTPException(status_code=404, detail="WebHook not found")
    return {
        "status_code": replay.status_code
    }
