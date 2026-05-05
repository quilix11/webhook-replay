from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_async_session
from src.services.webhook import save_webhook, get_all_webhooks

router = APIRouter()

async def intercept_data(request: Request):
    headers = dict(request.headers)

    try:
        data = await request.json()
    except Exception:
        data = None

    return{"headers": headers, "body": data}

@router.post("/webhooks/receive")
async def receive(payload: dict = Depends(intercept_data), session: AsyncSession = Depends(get_async_session)):
        
    saved_webhook = await save_webhook(session, payload["headers"], payload["body"])
    return {"status": "success", "id": saved_webhook.id}


@router.get("/webhooks/list")
async def list_webhooks(session: AsyncSession = Depends(get_async_session)):
    webhooks = await get_all_webhooks(session)
    return {"status": "success", "count": len(webhooks), "data": webhooks}