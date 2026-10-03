from uuid import UUID

from notification_service.exceptions import NotificationServiceError


class NotificationNotFoundError(NotificationServiceError):
    def __init__(self, notification_id: UUID) -> None:
        self.notification_id = notification_id
        super().__init__(f"Notification {notification_id} not found")
