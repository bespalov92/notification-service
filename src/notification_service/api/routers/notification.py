from typing import Annotated

from fastapi import APIRouter, Depends, status

from notification_service.api.dependencies import (
    get_notification_service,
)
from notification_service.api.schemas.common import ApiResponse
from notification_service.api.schemas.notification import (
    CreateNotificationRequest,
    NotificationResponse,
)
from notification_service.services.notification import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ApiResponse[NotificationResponse]
)
async def create_notification(
    request: CreateNotificationRequest,
    service: Annotated[
        NotificationService,
        Depends(get_notification_service)
    ]
) -> ApiResponse[NotificationResponse]:
    notification = await service.create(
        channel=request.channel,
        priority=request.priority,
        ttl=request.ttl,
        idempotency_key=request.idempotency_key,
        payload=request.payload,
    )

    return ApiResponse(
        data=NotificationResponse.model_validate(notification),
    )
