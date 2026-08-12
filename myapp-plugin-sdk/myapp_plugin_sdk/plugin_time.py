from typing import Protocol, runtime_checkable

from .plugin_base import PluginBase


@runtime_checkable
class PluginTime(PluginBase, Protocol):
    def get_time(self) -> str: ...
