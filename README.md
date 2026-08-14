# pyt-plugins

A demonstration of a Python plugin system with the following features.

* The host application can discover and load plugins at runtime using standard Python packaging (`importlib.metadata` entry points).
* The plugin system is kept in an SDK package separate from both the plugins and the application loading the plugins. This ensures that the app does not know about the plugin implementation and conversely that the plugins only know about the app interface.
* Plugins can have different types. Each plugin type share a common interface, but can also have additional functionality per type.
* The application can also has an interface, so the plugins can call functionality on the loading app.
* Two example plugin types and example implementations are provided.

## Repository layout

```
myapp-plugin-sdk/        SDK for plugin authors. Contains plugin and app interfaces
myapp-example-plugins1/  Example greeter plugin
myapp-example-plugins2/  Example timestamp plugin
myapp/                   Host application example
```

## Plugin SDK

`myapp-plugin-sdk` defines the contracts every plugin must satisfy using Python `Protocol` (structural subtyping — no inheritance required):

```
AppContext (Protocol)   log(level, message) · emit_event(name, data)

PluginBaseV1 (Protocol)   name · subsystem · load(ctx) · unload() · get_settings() · set_setting()
PluginBaseV2 (Protocol)   + get_tag(tag) · get_tags()
├── PluginGreeter           greet(target) → str
└── PluginTime              get_time() → str

PluginBase = PluginBaseV2   (alias — always points to the latest version)
```

`AppContext` is the **host interface** — the app implements it and passes it to `load()`. Plugins call back into the app through this object for logging, events, and any future host services.

- **`name`** — unique plugin identifier
- **`subsystem`** — `PluginType` enum value declaring which subsystem the plugin belongs to
- **`load(ctx)`** — async; called on startup with the host context; plugin stores `ctx` for later use
- **`unload()`** — async; called on shutdown to release resources
- **`get_settings()`** — returns a list of `PluginSetting` objects describing all configuration variables
- **`set_setting(name, value)`** — update a configuration variable by name; raises `KeyError` for unknown names, `TypeError` for wrong value types
- **`get_tag(tag)`** — capability query; returns `True`/`False` if the plugin explicitly supports or rejects a feature, or `None` if the tag is unrecognised (the app decides the default)
- **`get_tags()`** — returns a list of tag strings for which this plugin returns a non-`None` answer from `get_tag`; lets the host enumerate supported features without probing blindly
- **`greet()`** / **`get_time()`** — type-specific methods called by the host

`PluginType` is an `Enum` that can be expanded as support for more subsystems is added:

```python
class PluginType(Enum):
    GREETER = "greeter"
    TIME    = "time"
```

### PluginSetting

The app can get a list of whatever settings a plugin supports, and set them individually. Each setting is a dataclass with four fields:

| field | type | description |
|---|---|---|
| `name` | `str` | identifier used with `set_setting()` |
| `type` | `type` | expected Python type (`int`, `str`, …) |
| `description` | `str` | human-readable explanation |
| `value` | `Any` | current value |

## Writing a plugin

1. Install the SDK:
   ```bash
   pip install myapp-plugin-sdk
   ```

2. Implement the protocol — explicit inheritance is optional but recommended for IDE support:
   ```python
   from typing import Any
   from myapp_plugin_sdk import AppContext, PluginGreeter, PluginSetting, PluginType

   class MyPlugin(PluginGreeter):
       def __init__(self) -> None:
           self._ctx: AppContext | None = None
           self._settings: dict[str, PluginSetting] = {
               "prefix": PluginSetting("prefix", str, "Greeting prefix", "Hi"),
           }

       @property
       def name(self) -> str:
           return "my-plugin"

       @property
       def subsystem(self) -> PluginType:
           return PluginType.GREETER

       async def load(self, ctx: AppContext) -> None:
           self._ctx = ctx
           await ctx.log("info", f"{self.name} loaded.")

       async def unload(self) -> None:
           if self._ctx is not None:
               await self._ctx.log("info", f"{self.name} unloaded.")

       def get_settings(self) -> list[PluginSetting]:
           return list(self._settings.values())

       def set_setting(self, name: str, value: Any) -> None:
           if name not in self._settings:
               raise KeyError(f"Unknown setting: {name!r}")
           s = self._settings[name]
           if not isinstance(value, s.type):
               raise TypeError(f"{name!r} expects {s.type.__name__}")
           s.value = value

       def get_tag(self, tag: str) -> bool | None:
           tags = {"supports-html": False}
           return tags.get(tag)  # None for unrecognised tags

       def greet(self, target: str = "World") -> str:
           return f"{self._settings['prefix'].value}, {target}!"
   ```

3. Register the class as an entry point in your `pyproject.toml`:
   ```toml
   [project.entry-points."myapp.plugins"]
   my-plugin = "my_package.plugin:MyPlugin"
   ```

4. Install your plugin package and it will be discovered automatically by `myapp`.

## Setup

Install all packages in editable (development) mode from the repo root:

```bash
pip install -e myapp-plugin-sdk
pip install -e myapp-example-plugins1
pip install -e myapp-example-plugins2
```

## Running

```bash
cd myapp
python3 main.py
```

Expected output:

```
[INFO] greeter loaded.
[INFO] timestamp loaded.
Loaded 2 plugin(s).

[greeter] (greeter)
  prefix (str): 'Hello'  # Word or phrase before the target name
  punctuation (str): '!'  # Punctuation appended after the greeting
Hello, World! — from the Greeter plugin

[timestamp] (time)
  format (str): '%Y-%m-%dT%H:%M:%S'  # strftime format string
  utc_offset_hours (int): 0  # UTC offset in whole hours
Current time: 2026-08-12T12:00:00

[INFO] greeter unloaded.
[INFO] timestamp unloaded.
```

## Protocol versioning

The SDK uses an **additive versioning** scheme. Each new Protocol version extends the previous one so that a host built against a newer SDK can still load plugins built against an older SDK.

| Protocol | Adds |
|---|---|
| `PluginBaseV1` | Core contract: identity, lifecycle, settings |
| `PluginBaseV2` | Capability queries: `get_tag`, `get_tags` |

`PluginBase` is always an alias for the latest version and is what new plugin authors should use.

The host loader accepts any plugin that satisfies **`PluginBaseV1`** as a minimum. Before calling V2 methods it guards with `isinstance`:

```python
from myapp_plugin_sdk import PluginBaseV2

for plugin in plugins:
    if isinstance(plugin, PluginBaseV2):
        known_tags = plugin.get_tags()
        supports_html = plugin.get_tag("supports-html")
    else:
        known_tags = []
        supports_html = None  # V1 plugin — apply host default
```

To add a future **V3**, extend `PluginBaseV2`, reassign `PluginBase = PluginBaseV3`, and guard every new call with `isinstance(plugin, PluginBaseV3)`.

## Feature tags

`get_tag(tag)` lets the host query a plugin for optional capability flags without requiring a new Protocol method for every feature. The return value is a three-way signal:

| Return | Meaning |
|---|---|
| `True` | Plugin explicitly supports this feature |
| `False` | Plugin explicitly does not support this feature |
| `None` | Tag not recognised — the host applies its own default |

Example on the host side:

```python
DEFAULT_SUPPORTS_HTML = False

for plugin in plugins:
    supports_html = plugin.get_tag("supports-html")
    if supports_html is None:
        supports_html = DEFAULT_SUPPORTS_HTML
    if supports_html:
        render_html(plugin.greet())
    else:
        print(plugin.greet())
```

Example on the plugin side:

```python
def get_tag(self, tag: str) -> bool | None:
    tags: dict[str, bool] = {
        "supports-html": True,
        "supports-multiline": False,
    }
    return tags.get(tag)  # returns None for any unrecognised tag
```

## Type checking

```bash
./typecheck.sh
```

Runs [mypy](https://mypy-lang.org/) in strict mode across all packages. Install mypy first if needed:

```bash
pip install -r requirements-dev.txt
```

## How plugin discovery works

`myapp` does not know about any specific plugin package. At startup, `plugin_loader.py` calls:

```python
importlib.metadata.entry_points(group="myapp.plugins")
```

Python returns every entry point registered under that group across all installed packages. Each entry point is instantiated and checked against the `PluginBase` Protocol via `isinstance`. The loader creates a `DefaultAppContext` and passes it to `await plugin.load(ctx)`, giving each plugin a reference to the host interface. On exit, `await plugin.unload()` is called for every plugin.

`AppContext` is a Protocol — the app can provide any object that satisfies its signature. This makes the host interface easy to swap out or mock in tests.
