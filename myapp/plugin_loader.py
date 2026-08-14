from importlib.metadata import entry_points

from myapp_plugin_sdk import AppContext, PluginBaseV1


async def load_plugins(ctx: AppContext) -> list[PluginBaseV1]:
    """Discover all installed 'myapp.plugins' entry points and call load()."""
    plugins: list[PluginBaseV1] = []
    for ep in entry_points(group="myapp.plugins"):
        plugin = ep.load()()
        if not isinstance(plugin, PluginBaseV1):
            print(f"Warning: {ep.name!r} does not satisfy PluginBase protocol — skipped.")
            continue
        await plugin.load(ctx)
        plugins.append(plugin)
    return plugins


async def unload_plugins(plugins: list[PluginBaseV1]) -> None:
    for plugin in plugins:
        await plugin.unload()
