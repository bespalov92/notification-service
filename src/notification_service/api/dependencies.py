from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.session import get_session
from notification_service.plugins.registry import build_plugin_registry
from notification_service.services.notification import NotificationService


def get_notification_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NotificationService:
    return NotificationService(
        session=session,
        plugin_registry=build_plugin_registry()
    )
