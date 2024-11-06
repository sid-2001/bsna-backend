from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class User(BaseModel):
    id: uuid.UUID
    user_code: str
    first_name: str
    last_name: str
    email: str
    phone: str
    created_at: datetime
    role: str = "user"
    notification_token: str
    is_active: bool = True

class UserCreate(BaseModel):
    user_code: str
    first_name: str
    last_name: str
    email: str
    password: str
    phone: str
    notification_token: Optional[str] = ""

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""
    user_code: Optional[str] = ""
    notification_token: Optional[str] = ""