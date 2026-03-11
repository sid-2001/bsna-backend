from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects import postgresql as pg
from typing import Optional
from src.users import models


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
            nullable=True,
            default="NA"
        ),
        min_length=1,
        max_length=250
    )

    raised_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False
        )
    )

    fixed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=True
        )
    )

    status: str = Field(
        sa_column=Column(
            pg.ENUM("open", "closed", "attending", name="log_status"),
            nullable=False,
            default="open"
        )
    )

    attending_person: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.id"
    )

    attendee: Optional["models.User"] = Relationship(
        back_populates="alerts",
        sa_relationship_kwargs={"lazy": "selectin"}
    )