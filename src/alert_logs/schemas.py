from typing import Optional,List
from pydantic import BaseModel
from datetime import datetime
import uuid
from src.users.schema import User

class AlertLogsBase(BaseModel):
    uid: uuid.UUID
    driver_name: str
    transaction_count: int
    reason_of_abend: Optional[str] = "NA"
    raised_at: datetime
    fixed_at: Optional[datetime] = None
    status: str = "open"
    attending_person: Optional[uuid.UUID] = None
    
class AlertLogsUser(AlertLogsBase):   
    attendee: Optional[User] = None
    
class AlertLogsCreate(BaseModel):
    driver_name: str
    transaction_count: int
    reason_of_abend: Optional[str] = "NA"
    raised_at: Optional[datetime] = datetime.now()
    
class AlertLogsUpdate(BaseModel):
    driver_name: Optional[str]
    transaction_count: Optional[int]
    reason_of_abend: Optional[str]
    raised_at: Optional[datetime]
    fixed_at: Optional[datetime]
    closed_by: Optional[uuid.UUID]
    status: Optional[str]
    attending_person: Optional[uuid.UUID]
    
