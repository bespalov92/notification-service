from notification_service.config import get_settings
from notification_service.domain.enums import NotificationChannel
from notification_service.plugins.base import NotificationPlugin
from notification_service.plugins.email import EmailPlugin
from notification_service.plugins.exceptions import (
    PluginAlreadyRegisteredError,
    PluginNotFoundError,
)
from notification_service.plugins.fake import FakePlugin


class PluginRegistry:
    """
    A centralized registry for dynamically managing and retrieving
    notification plugins.

    This registry maps specific notification channels (e.g., Email, SMS)
    to their corresponding plugin implementations.
    """

    def __init__(self) -> None:
        self._plugins: dict[NotificationChannel, NotificationPlugin] = {}

    def register(self, plugin: NotificationPlugin) -> None:
        if plugin.channel in self._plugins:
            raise PluginAlreadyRegisteredError(plugin.channel)

        self._plugins[plugin.channel] = plugin

    def get(self, channel: NotificationChannel) -> NotificationPlugin:
        plugin = self._plugins.get(channel)

        if plugin is None:
            raise PluginNotFoundError(channel)

        return plugin


def build_plugin_registry() -> PluginRegistry:
    settings = get_settings()

    registry = PluginRegistry()
    registry.register(EmailPlugin(settings.smtp))
    registry.register(FakePlugin(NotificationChannel.SMS))
    registry.register(FakePlugin(NotificationChannel.PUSH))

    return registry
