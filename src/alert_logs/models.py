from sqlmodel import SQLModel, Field, Column
from datetime import datetime
import uuid
from sqlalchemy.dialects import postgresql as pg
from typing import Optional

class AlertLogs(SQLModel, table=True):
    __tablename__ = "logs"
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            default=uuid.uuid4,
            index=True,
            primary_key=True
        )
    )
    driver_name: str = Field(
        sa_column=Column(
            pg.TEXT,
            nullable=False,
            index=True,
        ),
        min_length=4,
        max_length=12
    )
    transaction_count: int = Field(
        sa_column=Column(
            pg.INTEGER,
            nullable=False
        )
    )
    reason_of_abend: str = Field(
        sa_column=Column(
            pg.TEXT,
            nullable=True
        ),
        min_length=1,
        max_length=250
    )
    raised_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=False),
            nullable=False,
            default=datetime.now()
        )
    )
    fixed_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=False),
            nullable=True
        )
    )
    closed_by: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.id"
    )
    status: str = Field(
        sa_column=Column(
            pg.ENUM("open","closed","attending", name="log_status"),
            nullable=False,
            default="open"
        )
    )
    attending_person: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.id"
    )