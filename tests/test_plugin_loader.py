from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app_context import DefaultAppContext
from plugin_loader import load_plugins, unload_plugins
from myapp_plugin_sdk import PluginBase


@pytest.fixture
def ctx() -> DefaultAppContext:
    return DefaultAppContext()


async def test_load_plugins_no_entry_points(ctx: DefaultAppContext) -> None:
    with patch("plugin_loader.entry_points", return_value=[]):
        assert await load_plugins(ctx) == []


async def test_load_plugins_invokes_load(ctx: DefaultAppContext) -> None:
    plugin = MagicMock(spec=PluginBase)
    plugin.load = AsyncMock()
    ep = MagicMock()
    ep.load.return_value = lambda: plugin

    with patch("plugin_loader.entry_points", return_value=[ep]):
        result = await load_plugins(ctx)

    plugin.load.assert_awaited_once_with(ctx)
    assert result == [plugin]


async def test_load_plugins_skips_non_protocol(
    ctx: DefaultAppContext, capsys: pytest.CaptureFixture[str]
) -> None:
    class NotAPlugin:
        pass

    ep = MagicMock()
    ep.name = "bad"
    ep.load.return_value = NotAPlugin

    with patch("plugin_loader.entry_points", return_value=[ep]):
        result = await load_plugins(ctx)

    assert result == []
    assert "skipped" in capsys.readouterr().out


async def test_unload_plugins_calls_unload() -> None:
    plugin = MagicMock(spec=PluginBase)
    plugin.unload = AsyncMock()

    await unload_plugins([plugin])

    plugin.unload.assert_awaited_once()


async def test_unload_plugins_empty_list() -> None:
    await unload_plugins([])  # must not raise
