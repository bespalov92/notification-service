import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from notification_service.db.session import (
    engine,
    session_maker,
)


def test_postgres_driver() -> None:
    assert isinstance(engine, AsyncEngine)
    assert engine.dialect.driver == "asyncpg"


@pytest.mark.asyncio
async def test_session_maker_creates_async_session() -> None:
    async with session_maker() as session:
        assert isinstance(session, AsyncSession)
