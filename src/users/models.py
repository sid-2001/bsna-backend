from sqlmodel import SQLModel, Field, Column
from datetime import datetime
import uuid
from sqlalchemy.dialects import postgresql as pg

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    user_code: str = Field(
        sa_column=Column(
            pg.TEXT,
            nullable=False,
            unique=True,
            index=True
        )
    )
    first_name: str
    last_name: str
    email: str
    password: str = Field(
        exclude=True,
        sa_column=Column(
            pg.TEXT,
            nullable=True,
            default="hashed-pass-remove-entry",
        )
    )
    password_hash: str = Field(
        exclude=True,
        sa_column=Column(
            pg.TEXT,
            nullable=True,
            default="hashed-pass-remove-entry",
        )
    )
    phone: str
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=False),
            nullable=False,
            default=datetime.now()
        )
    )
    role: str = Field(
        sa_column=Column(
            pg.ENUM("admin","user", name="user_role"),
            nullable=False,
            default="user"
        )
    )
    notification_token: str = Field(
        sa_column=Column(
            pg.TEXT,
            nullable=True
        )
    )
    is_active: bool = Field(
        sa_column=Column(
            pg.BOOLEAN,
            nullable=False,
            default=True
        )
    )
    
    