import os
import importlib
from typing import Dict, Any, Type
from .base import DataSourcePlugin

class DataSourceManager:
    """
    Manages the discovery, loading, and access of data source plugins.
    """
    def __init__(self, plugins_dir: str = "Three_PointO_ArchE/data_sources/plugins"):
        self.plugins: Dict[str, Type[DataSourcePlugin]] = {}
        self.plugins_dir = plugins_dir
        self._discover_plugins()

    def _discover_plugins(self):
        """
        Dynamically discovers and loads plugins from the plugins directory.
        """
        if not os.path.exists(self.plugins_dir):
            return

        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module_path = f"Three_PointO_ArchE.data_sources.plugins.{module_name}"
                try:
                    module = importlib.import_module(module_path)
                    for attribute_name in dir(module):
                        attribute = getattr(module, attribute_name)
                        if isinstance(attribute, type) and issubclass(attribute, DataSourcePlugin) and attribute is not DataSourcePlugin:
                            plugin_id = module_name.replace("_plugin", "")
                            self.plugins[plugin_id] = attribute
                            print(f"Discovered plugin: {plugin_id}")
                except Exception as e:
                    print(f"Failed to load plugin {module_name}: {e}")

    def get_plugin(self, plugin_id: str) -> Type[DataSourcePlugin]:
        """
        Retrieves a loaded plugin class by its ID.
        """
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            raise ValueError(f"Plugin '{plugin_id}' not found.")
        return plugin
