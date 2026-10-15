from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from pytest import MonkeyPatch

from notification_service.messaging import tasks
from notification_service.services.exceptions import RetryableDeliveryError


def test_deliver_notification_runs_async_delivery(
    monkeypatch: MonkeyPatch,
) -> None:
    notification_id = uuid4()
    run_delivery = AsyncMock()

    monkeypatch.setattr(
        tasks,
        "run_delivery",
        run_delivery,
    )

    tasks.deliver_notification.run(str(notification_id))

    run_delivery.assert_awaited_once_with(notification_id)


def test_deliver_notification_retries_retryable_failure(
    monkeypatch: MonkeyPatch,
) -> None:
    notification_id = uuid4()
    error = RetryableDeliveryError(notification_id)

    run_delivery = AsyncMock(side_effect=error)
    retry = Mock(side_effect=RuntimeError("retry scheduled"))

    monkeypatch.setattr(tasks, "run_delivery", run_delivery)
    monkeypatch.setattr(
        tasks.deliver_notification,
        "retry",
        retry,
    )

    with pytest.raises(RuntimeError, match="retry scheduled"):
        tasks.deliver_notification.run(str(notification_id))

    retry.assert_called_once_with(
        exc=error,
        countdown=5,
    )
    run_delivery.assert_awaited_once_with(notification_id)
