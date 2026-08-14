from datetime import datetime, timedelta, timezone
from typing import Any

from myapp_plugin_sdk import AppContext, PluginSetting, PluginTime, PluginType


class TimestampPlugin(PluginTime):
    def __init__(self) -> None:
        self._ctx: AppContext | None = None
        self._settings: dict[str, PluginSetting] = {
            "format":           PluginSetting("format",           str, "strftime format string",   "%Y-%m-%dT%H:%M:%S"),
            "utc_offset_hours": PluginSetting("utc_offset_hours", int, "UTC offset in whole hours", 0),
        }

    @property
    def name(self) -> str:
        return "timestamp"

    @property
    def subsystem(self) -> PluginType:
        return PluginType.TIME

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

    def get_tag(self, tag: str) -> bool | None:
        return None

    def get_time(self) -> str:
        tz  = timezone(timedelta(hours=self._settings["utc_offset_hours"].value))
        fmt = self._settings["format"].value
        return datetime.now(tz).strftime(fmt)
