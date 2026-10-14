from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from notification_service.api.dependencies import (
    get_notification_service,
)
from notification_service.api.schemas.common import ApiResponse
from notification_service.api.schemas.notification import (
    CreateNotificationRequest,
    NotificationListParams,
    NotificationResponse,
)
from notification_service.services.notification import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ApiResponse[NotificationResponse],
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApiResponse[None],
            "description": (
                "Request structure or payload validation failed"
            ),
        },
    },
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


@router.get(
    "",
    response_model=ApiResponse[list[NotificationResponse]],
)
async def list_notifications(
    service: Annotated[
        NotificationService,
        Depends(get_notification_service),
    ],
    params: Annotated[
        NotificationListParams,
        Query()
    ]
) -> ApiResponse[list[NotificationResponse]]:
    notifications, total = await service.get_page(
        limit=params.limit,
        offset=params.offset,
        channel=params.channel,
        status=params.status,
        created_from=params.created_from,
        created_to=params.created_to,
    )

    return ApiResponse(
        data=[
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ],
        meta={
            "limit": params.limit,
            "offset": params.offset,
            "total": total,
        },
    )


@router.get(
    "/{notification_id:uuid}",
    response_model=ApiResponse[NotificationResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ApiResponse[None],
            "description": "Notification not found",
        },
    },
)
async def get_notification(
    notification_id: UUID,
    service: Annotated[
        NotificationService,
        Depends(get_notification_service),
    ]
) -> ApiResponse[NotificationResponse]:
    notification = await service.get_by_id(notification_id)

    return ApiResponse(
        data=NotificationResponse.model_validate(notification)
    )
