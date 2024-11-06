from typing import Optional,List
from pydantic import BaseModel
from datetime import datetime
import uuid

class AlertLogsBase(BaseModel):
    uid: uuid.UUID
    driver_name: str
    transaction_count: int 
    reason_of_abend: str
    raised_at: Optional[datetime] = None
    fixed_at: Optional[datetime] = None
    closed_by: Optional[uuid.UUID] = None
    status: str 
    attending_person: Optional[uuid.UUID] = None
    
class AlertLogsCreate(BaseModel):
    driver_name: str
    transaction_count: int
    reason_of_abend: Optional[str]
    raised_at: Optional[datetime]
    
class AlertLogsUpdate(BaseModel):
    driver_name: Optional[str]
    transaction_count: Optional[int]
    reason_of_abend: Optional[str]
    raised_at: Optional[datetime]
    fixed_at: Optional[datetime]
    closed_by: Optional[uuid.UUID]
    status: Optional[str]
    attending_person: Optional[uuid.UUID]
    
