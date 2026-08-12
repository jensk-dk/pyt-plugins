from typing import Protocol, runtime_checkable

from .plugin_base import PluginBase


@runtime_checkable
class PluginGreeter(PluginBase, Protocol):
    def greet(self, target: str = "World") -> str: ...
