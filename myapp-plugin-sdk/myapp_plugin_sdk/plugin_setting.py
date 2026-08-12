from dataclasses import dataclass
from typing import Any


@dataclass
class PluginSetting:
    name: str
    type: type[Any]
    description: str
    value: Any
