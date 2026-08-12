"""
myapp — plugin-capable application.

Quick start:
    pip install -e ../myapp-plugin-sdk
    pip install -e ../myapp-example-plugins1
    pip install -e ../myapp-example-plugins2
    python main.py
"""
import asyncio

from app_context import DefaultAppContext
from plugin_loader import load_plugins, unload_plugins
from myapp_plugin_sdk import PluginGreeter, PluginTime


async def main() -> None:
    ctx = DefaultAppContext()
    plugins = await load_plugins(ctx)
    if not plugins:
        print("No plugins found. Install plugins and re-run.")
        return

    print(f"Loaded {len(plugins)} plugin(s).\n")
    try:
        for plugin in plugins:
            print(f"[{plugin.name}] ({plugin.subsystem.value})")
            for s in plugin.get_settings():
                print(f"  {s.name} ({s.type.__name__}): {s.value!r}  # {s.description}")
            if isinstance(plugin, PluginGreeter):
                print(plugin.greet())
            elif isinstance(plugin, PluginTime):
                print(f"Current time: {plugin.get_time()}")
            print()
    finally:
        await unload_plugins(plugins)


if __name__ == "__main__":
    asyncio.run(main())
