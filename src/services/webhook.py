from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.webhook import WebHook
import httpx

async def save_webhook(session: AsyncSession, headers: dict, payload: dict):
    webhook = WebHook(headers= headers, payload= payload)
    session.add(webhook)
    await session.commit()
    await session.refresh(webhook)

    return webhook

async def get_all_webhooks(session: AsyncSession):
    query = select(WebHook).order_by(WebHook.id.desc())
    result = await session.execute(query)
    
    return result.scalars().all()

async def replay_webhooks(session: AsyncSession, webhook_id, target_url):
    result = await session.execute(select(WebHook).where(WebHook.id == webhook_id))
    webhook = result.scalar_one_or_none()
    async with httpx.AsyncClient() as client:
        result = await client.post(target_url, json=webhook.payload, headers=webhook.headers)
    return result

        