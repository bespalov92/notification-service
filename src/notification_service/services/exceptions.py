from uuid import UUID

from notification_service.exceptions import NotificationServiceError


class NotificationNotFoundError(NotificationServiceError):
    """Raised when a notification cannot be found by its identifier"""

    def __init__(self, notification_id: UUID) -> None:
        self.notification_id = notification_id
        super().__init__(f"Notification {notification_id} not found")


class RetryableDeliveryError(NotificationServiceError):
    """Raised when a failed notification delivery should be retried"""

    def __init__(self, notification_id: UUID) -> None:
        self.notification_id = notification_id
        super().__init__(
            f"Notification {notification_id} delivery can be retried"
        )
