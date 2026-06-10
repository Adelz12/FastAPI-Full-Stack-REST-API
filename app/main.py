from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.database import engine, Base, get_db
from app.deps import get_redis, redis_pool
from app.router import auth, items

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    # 1. Automatic Database Migrations: Create tables on startup if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Verify Redis Connectivity on startup
    try:
        redis_client = Redis(connection_pool=redis_pool)
        await redis_client.ping()
        await redis_client.close()
    except Exception as e:
        print(f"Warning: Failed to connect to Redis on startup: {e}")

    yield

    # Shutdown actions
    # 1. Disconnect Redis pool
    await redis_pool.disconnect()
    # 2. Dispose of SQLAlchemy engine
    await engine.dispose()

app = FastAPI(
    title="FastAPI Full-Stack REST API",
    description="A production-ready Python REST API built with FastAPI, backed by PostgreSQL and Redis.",
    version="1.0.0",
    lifespan=lifespan
)

# Register routers
app.include_router(auth.router)
app.include_router(items.router)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Health check endpoint to verify database and Redis connectivity."""
    db_status = "unhealthy"
    redis_status = "unhealthy"

    # Test Database
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        pass

    # Test Redis
    try:
        await redis.ping()
        redis_status = "healthy"
    except Exception:
        pass

    # If any service is unhealthy, return a 503 service unavailable
    if db_status != "healthy" or redis_status != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": db_status,
                "redis": redis_status
            }
        )

    return {
        "status": "healthy",
        "database": db_status,
        "redis": redis_status
    }
