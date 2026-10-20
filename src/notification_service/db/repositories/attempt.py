from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.models.attempt import Attempt


class AttemptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, attempt: Attempt) -> None:
        self._session.add(attempt)
        await self._session.flush()

    async def get_by_notification_id(
        self,
        notification_id: UUID
    ) -> list[Attempt]:
        stmt = (
            select(Attempt)
            .where(Attempt.notification_id == notification_id)
            .order_by(
                Attempt.created_at.asc(),
                Attempt.id.asc()
            )
        )

        return list((await self._session.scalars(stmt)).all())
