from fastapi import FastAPI, Header
from pydantic import BaseModel
from contextlib import asynccontextmanager

from src.db.main import init_db
from src.users.routes import user_router
from src.auth.routes import auth_router
from src.drivers.routes import driver_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    await init_db()
    print("Connected to Postgres")
    yield
    print("Shutting down application...")

app = FastAPI(
    title="BSNA Monitoring Application Server",
    version="version-1.0",
    description="This is a monitoring application server for BSNA Drivers",
    lifespan=lifespan
)

# add user_router
app.include_router(user_router,prefix="/api/v1/users",tags=["users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(driver_router, prefix="/api/v1/drivers", tags=["drivers"])
