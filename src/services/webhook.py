from sqlalchemy.ext.asyncio import AsyncSession
from src.models.webhook import WebHook

async def save_webhook(session: AsyncSession, headers: dict, payload: dict):
    webhook = WebHook(headers= headers, payload= payload)
    session.add(webhook)
    await session.commit()
    await session.refresh(webhook)

    return webhook