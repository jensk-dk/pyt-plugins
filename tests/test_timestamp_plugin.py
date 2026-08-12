import re
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest

from myapp_example_plugin2.plugin import TimestampPlugin
from myapp_plugin_sdk import PluginType


@pytest.fixture
async def plugin() -> AsyncGenerator[TimestampPlugin, None]:
    p = TimestampPlugin()
    ctx = MagicMock()
    ctx.log = AsyncMock()
    await p.load(ctx)
    yield p
    await p.unload()


def test_name() -> None:
    assert TimestampPlugin().name == "timestamp"


def test_subsystem() -> None:
    assert TimestampPlugin().subsystem == PluginType.TIME


def test_get_time_default_format(plugin: TimestampPlugin) -> None:
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", plugin.get_time())


def test_get_time_custom_format(plugin: TimestampPlugin) -> None:
    plugin.set_setting("format", "%Y")
    assert re.fullmatch(r"\d{4}", plugin.get_time())


def test_set_setting_wrong_type_raises(plugin: TimestampPlugin) -> None:
    with pytest.raises(TypeError):
        plugin.set_setting("utc_offset_hours", "not-an-int")


def test_set_setting_unknown_raises(plugin: TimestampPlugin) -> None:
    with pytest.raises(KeyError):
        plugin.set_setting("nonexistent", 0)


def test_get_settings_names(plugin: TimestampPlugin) -> None:
    assert {s.name for s in plugin.get_settings()} == {"format", "utc_offset_hours"}


async def test_load_calls_ctx_log() -> None:
    p = TimestampPlugin()
    ctx = MagicMock()
    ctx.log = AsyncMock()
    await p.load(ctx)
    ctx.log.assert_awaited_once_with("info", "timestamp loaded.")
    await p.unload()


async def test_unload_calls_ctx_log() -> None:
    p = TimestampPlugin()
    ctx = MagicMock()
    ctx.log = AsyncMock()
    await p.load(ctx)
    ctx.log.reset_mock()
    await p.unload()
    ctx.log.assert_awaited_once_with("info", "timestamp unloaded.")
