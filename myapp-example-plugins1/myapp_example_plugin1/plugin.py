from typing import Any

from myapp_plugin_sdk import AppContext, PluginGreeter, PluginSetting, PluginType


class GreeterPlugin(PluginGreeter):
    def __init__(self) -> None:
        self._ctx: AppContext | None = None
        self._settings: dict[str, PluginSetting] = {
            "prefix":      PluginSetting("prefix",      str, "Word or phrase before the target name", "Hello"),
            "punctuation": PluginSetting("punctuation", str, "Punctuation appended after the greeting", "!"),
        }

    @property
    def name(self) -> str:
        return "greeter"

    @property
    def subsystem(self) -> PluginType:
        return PluginType.GREETER

    async def load(self, ctx: AppContext) -> None:
        self._ctx = ctx
        await ctx.log("info", f"{self.name} loaded.")

    async def unload(self) -> None:
        if self._ctx is not None:
            await self._ctx.log("info", f"{self.name} unloaded.")
        self._ctx = None

    def get_settings(self) -> list[PluginSetting]:
        return list(self._settings.values())

    def set_setting(self, name: str, value: Any) -> None:
        if name not in self._settings:
            raise KeyError(f"Unknown setting: {name!r}")
        s = self._settings[name]
        if not isinstance(value, s.type):
            raise TypeError(f"{name!r} expects {s.type.__name__}, got {type(value).__name__}")
        s.value = value

    def greet(self, target: str = "World") -> str:
        prefix = self._settings["prefix"].value
        punct  = self._settings["punctuation"].value
        return f"{prefix}, {target}{punct} — from the Greeter plugin"
