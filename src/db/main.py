import logging
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

# Suppress SQLAlchemy logs
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

# Async database URL (with asyncpg)
DATABASE_URL = 'postgresql+asyncpg://doadmin:AVNS_xzyC5HsXTawenfBh8Y4@db-postgresql-blr1-15255-do-user-19732516-0.m.db.ondigitalocean.com:25060/bsna_dev'

# Create async engine
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)

# Initialize the database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Get DB session
async def get_session() -> AsyncSession:  # type: ignore
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session