from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.app_config import settings

engine = create_async_engine(settings.DATABASE_URL)

async_session_factory = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_async_session():
    async with async_session_factory() as session:
        yield session
