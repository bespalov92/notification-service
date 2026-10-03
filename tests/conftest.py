from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.session import engine, get_session, session_maker
from notification_service.main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with engine.connect() as connection:
        transaction = await connection.begin()

        async with session_maker(
            bind=connection,
            join_transaction_mode="create_savepoint",
        ) as session:
            yield session

        await transaction.rollback()


@pytest.fixture
async def api_client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient]:
    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_session, None)
