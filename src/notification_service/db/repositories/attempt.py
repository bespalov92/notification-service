from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.attempt import Attempt


class AttemptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, attempt: Attempt) -> None:
        self._session.add(attempt)
        await self._session.flush()
