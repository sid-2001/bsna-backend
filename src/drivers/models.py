from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects import postgresql as pg
from datetime import datetime
import uuid

class Driver(SQLModel, table=True):
    __tablename__ = "drivers"
    
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            default=uuid.uuid4,
            index=True,
            primary_key=True
        )
    )
    name: str = Field(
        sa_column=Column(
            pg.TEXT,
            nullable=False,
            index=True,
            unique=False
        )
    )
    transaction_count: int = Field(
        sa_column=Column(
            pg.INTEGER,
            nullable=False,
            default=0
        )
    )
    is_Active: bool = Field(
        sa_column=Column(
            pg.BOOLEAN,
            nullable=False,
            default=True
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=False),
            nullable=False,
            default=datetime.now()
        )
    )
    description: str = Field(
        sa_column=Column(
            pg.TEXT,
            nullable=True
        )
    )
    valid_users: list[uuid.UUID] = Field(
        sa_column=Column(
            pg.ARRAY(pg.UUID),
            nullable=True,
            default=[]
        )
    )

