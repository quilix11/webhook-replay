from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import func
from datetime import datetime


class Base(DeclarativeBase):
    pass



class WebHook(Base):

    __tablename__ = "webhooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    headers: Mapped[dict] = mapped_column(JSONB)
    event_name: Mapped[str | None]
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())