from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from pytest import MonkeyPatch

from notification_service.messaging import tasks


async def test_publish_delivery_task_sends_celery_task(
    monkeypatch: MonkeyPatch,
) -> None:
    notification_id = uuid4()
    delay = Mock()

    monkeypatch.setattr(
        tasks.deliver_notification,
        "delay",
        delay,
    )

    await tasks.publish_delivery_task(notification_id)

    delay.assert_called_once_with(str(notification_id))


def test_publish_outbox_events_runs_async_relay(
    monkeypatch: MonkeyPatch,
) -> None:
    run_outbox_relay = AsyncMock(return_value=2)

    monkeypatch.setattr(
        tasks,
        "run_outbox_relay",
        run_outbox_relay,
    )

    result = tasks.publish_outbox_events.run()

    assert result == 2
    run_outbox_relay.assert_awaited_once_with()
