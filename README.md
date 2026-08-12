# pyt-plugins

A demonstration of a Python plugin system with the following features.

* The host application can discover and load plugins at runtime using standard Python packaging (`importlib.metadata` entry points).
* The plugin system is kept in an SDK package separate from both the plugins and the application loading the plugins. This ensures that the app does not know about the plugin implementation and conversely that the plugins only know about the app interface.
* Plugins can have different types. Each plugin type share a common interface, but can also have additional functionality per type.
* The application can also has and interface, so the plugins can call functionality on the loading app.
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

PluginBase (Protocol)   name · subsystem · load(ctx) · unload() · get_settings() · set_setting()
├── PluginGreeter       greet(target) → str
└── PluginTime          get_time() → str
```

`AppContext` is the **host interface** — the app implements it and passes it to `load()`. Plugins call back into the app through this object for logging, events, and any future host services.

- **`name`** — unique plugin identifier
- **`subsystem`** — `PluginType` enum value declaring which subsystem the plugin belongs to
- **`load(ctx)`** — async; called on startup with the host context; plugin stores `ctx` for later use
- **`unload()`** — async; called on shutdown to release resources
- **`get_settings()`** — returns a list of `PluginSetting` objects describing all configuration variables
- **`set_setting(name, value)`** — update a configuration variable by name; raises `KeyError` for unknown names, `TypeError` for wrong value types
- **`greet()`** / **`get_time()`** — type-specific methods called by the host

`PluginType` is an `Enum` that can be expanded as support for more subsystems is added:

```python
class PluginType(Enum):
    GREETER = "greeter"
    TIME    = "time"
```

### PluginSetting

Each setting is a dataclass with four fields:

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
