import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis import Redis
from sqlmodel import SQLModel

# Import the database engine we created in db.py
from app.db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This automatically builds your SQLite tables inside the container on boot
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(
    title="E-Commerce Ordering & Payment API Engine",
    description="Backend Job Assessment Infrastructure Spec",
    version="1.0.0",
    lifespan=lifespan,
)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)


@app.get("/health", tags=["Infrastructure Health"])
def system_health_check():
    try:
        redis_alive = "healthy" if redis_client.ping() else "unhealthy"
    except Exception as error:
        redis_alive = f"unreachable: {str(error)}"

    return {
        "status": "online",
        "environment": os.getenv("ENV_MODE", "unknown"),
        "services": {"api_gateway": "running", "redis_cache": redis_alive},
    }
