from sqlmodel import create_engine,text,SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.users.models import User
from src.drivers.models import Driver
from src.alert_logs.models import AlertLogs

engine = AsyncEngine(
    create_engine(
    url=Config.DB_URL,
    echo=True
))

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(
            SQLModel.metadata.create_all
        )

# define the database session object
async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with Session() as session:
        yield session