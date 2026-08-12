from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest

from myapp_example_plugin1.plugin import GreeterPlugin
from myapp_plugin_sdk import PluginType


@pytest.fixture
async def plugin() -> AsyncGenerator[GreeterPlugin, None]:
    p = GreeterPlugin()
    ctx = MagicMock()
    ctx.log = AsyncMock()
    await p.load(ctx)
    yield p
    await p.unload()


def test_name() -> None:
    assert GreeterPlugin().name == "greeter"


def test_subsystem() -> None:
    assert GreeterPlugin().subsystem == PluginType.GREETER


def test_greet_default(plugin: GreeterPlugin) -> None:
    assert plugin.greet() == "Hello, World! — from the Greeter plugin"


def test_greet_custom_target(plugin: GreeterPlugin) -> None:
    assert plugin.greet("Alice") == "Hello, Alice! — from the Greeter plugin"


def test_set_setting_prefix(plugin: GreeterPlugin) -> None:
    plugin.set_setting("prefix", "Hi")
    assert plugin.greet() == "Hi, World! — from the Greeter plugin"


def test_set_setting_punctuation(plugin: GreeterPlugin) -> None:
    plugin.set_setting("punctuation", ".")
    assert plugin.greet() == "Hello, World. — from the Greeter plugin"


def test_set_setting_wrong_type_raises(plugin: GreeterPlugin) -> None:
    with pytest.raises(TypeError):
        plugin.set_setting("prefix", 42)


def test_set_setting_unknown_raises(plugin: GreeterPlugin) -> None:
    with pytest.raises(KeyError):
        plugin.set_setting("nonexistent", "value")


def test_get_settings_names(plugin: GreeterPlugin) -> None:
    assert {s.name for s in plugin.get_settings()} == {"prefix", "punctuation"}


async def test_load_calls_ctx_log() -> None:
    p = GreeterPlugin()
    ctx = MagicMock()
    ctx.log = AsyncMock()
    await p.load(ctx)
    ctx.log.assert_awaited_once_with("info", "greeter loaded.")
    await p.unload()


async def test_unload_calls_ctx_log() -> None:
    p = GreeterPlugin()
    ctx = MagicMock()
    ctx.log = AsyncMock()
    await p.load(ctx)
    ctx.log.reset_mock()
    await p.unload()
    ctx.log.assert_awaited_once_with("info", "greeter unloaded.")
