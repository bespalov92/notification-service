from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.session import engine, session_maker


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
