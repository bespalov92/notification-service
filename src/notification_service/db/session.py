from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from notification_service.config import get_settings

settings = get_settings()

engine = create_async_engine(
    url=str(settings.postgres.dsn),
    pool_pre_ping=True
)

session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        yield session


async def dispose_database() -> None:
    await engine.dispose()
