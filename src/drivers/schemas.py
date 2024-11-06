from typing import Optional,List
from pydantic import BaseModel
from datetime import datetime
import uuid

class DriverBase(BaseModel):
    uid: uuid.UUID
    name: str
    transaction_count: int 
    description: Optional[str]
    is_Active: bool 
    updated_at: datetime
    
class DriverCreate(BaseModel):
    name: str
    transaction_count: int
    description: Optional[str]
    is_Active: bool
    
class DriverUpdate(BaseModel):
    name: Optional[str]
    transaction_count: Optional[int]
    description: Optional[str]
    is_Active: Optional[bool]
    updated_at: Optional[datetime] = datetime.now()
    
class DriverUpdateCount(BaseModel):
    name: str
    transaction_count: int
    description: Optional[str]
    updated_at: datetime = datetime.now()