from unittest.mock import AsyncMock
from uuid import uuid4

from pytest import MonkeyPatch

from notification_service.domain.enums import NotificationChannel
from notification_service.messaging import tasks


def test_build_plugin_registry_registers_every_channel() -> None:
    registry = tasks.build_plugin_registry()

    for channel in NotificationChannel:
        plugin = registry.get(channel)

        assert plugin.channel is channel
        assert plugin.provider_name == "fake"


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
