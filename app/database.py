from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Create the asynchronous engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True if we want to log all generated SQL queries
    future=True
)

# Create the session maker bound to our async engine
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Define the declarative base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Async database session generator dependency
async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
