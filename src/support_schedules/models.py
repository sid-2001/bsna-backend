from sqlmodel import SQLModel, Column, Field, Relationship
from datetime import datetime
from typing import List, TYPE_CHECKING,Optional
import uuid
from sqlalchemy.dialects.postgresql import UUID as pgUUID, ENUM, TIMESTAMP
from src.users import models


class UserScheduleLink(SQLModel, table=True):
    __tablename__ = "user_schedule_link"
    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    schedule_id: uuid.UUID = Field(foreign_key="support_schedule.uid", primary_key=True)


class SupportSchedule(SQLModel, table=True):
    __tablename__ = "support_schedule"

    uid: uuid.UUID = Field(
        sa_column=Column(pgUUID, nullable=False, default=uuid.uuid4, primary_key=True, index=True)
    )
    start_date: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )
    end_date: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )
    environment: str = Field(
        sa_column=Column(
            ENUM("production", "uat", name="schedule_environment"),
            nullable=False,
            default="uat",
        )
    )
    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    )
    
    # user_ids: Optional[List[str]] = Field(
    #     default=None,
    #     foreign_key='models.User.id'
    # )

    # users: Optional[List['models.User']] = Relationship(
    #     back_populates="schedules",
    #     link_model=UserScheduleLink
    # )
