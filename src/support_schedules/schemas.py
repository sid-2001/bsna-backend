from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid

from src.users.models import User



class SupportScheduleBase(BaseModel):
    uid: uuid.UUID
    start_date: datetime
    end_date: datetime
    environment: str
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d")
        }
    
class SupportScheduleUser(SupportScheduleBase):
    users: Optional[List[User]] = []
    
    class Config:
        orm_mode = True
    
class SupportScheduleCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    environment: str
    users: Optional[List[str]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d")
        }
    
class SupportScheduleUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    environment: Optional[str] = None
    users: Optional[List[str]] = []