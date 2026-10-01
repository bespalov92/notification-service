from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.session import session_maker


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
