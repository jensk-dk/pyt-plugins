from typing import Any, Protocol, runtime_checkable

from .app_context import AppContext
from .plugin_setting import PluginSetting
from .plugin_type import PluginType


@runtime_checkable
class PluginBase(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def subsystem(self) -> PluginType: ...

    async def load(self, ctx: AppContext) -> None: ...
    async def unload(self) -> None: ...

    def get_settings(self) -> list[PluginSetting]: ...
    def set_setting(self, name: str, value: Any) -> None: ...
