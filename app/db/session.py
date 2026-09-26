from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Shared declarative base — every model inherits from this."""

    pass


async def get_db():
    """
    FastAPI dependency: yields a session for the duration of one request,
    then always closes it, even if the request raised an exception.
    """
    async with AsyncSessionLocal() as session:
        yield session
