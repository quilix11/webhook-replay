from pydantic import BaseModel, EmailStr
from typing import Any
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class WebhookCreate(BaseModel):
    headers: dict[str, Any]
    payload: dict[str, Any]