import glob
import importlib.util
import os
from types import ModuleType
from typing import List, Optional, Type

from dotbot.plugin import Plugin

# We keep references to loaded modules so they don't get garbage collected.
loaded_modules = []


def load(path: str) -> List[Type[Plugin]]:
    basename = os.path.basename(path)
    module_name, extension = os.path.splitext(basename)
    loaded_module = load_module(module_name, path)
    plugins = []
    for name in dir(loaded_module):
        possible_plugin = getattr(loaded_module, name)
        try:
            if issubclass(possible_plugin, Plugin) and possible_plugin is not Plugin:
                plugins.append(possible_plugin)
        except TypeError:
            pass
    loaded_modules.append(loaded_module)
    return plugins


def load_module(module_name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        msg = f"Unable to load module {module_name} from {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_plugins(paths: List[str], plugins: Optional[List[Type[Plugin]]] = None) -> List[Type[Plugin]]:
    """
    Load plugins from the given paths and add them to the given list of plugins.

    Args:
        paths: List of file paths to load plugins from. Each path can be either a file or a directory.
        plugins: List of existing plugins to add to.

    Returns the newly-loaded plugins.
    """
    if plugins is None:
        plugins = []
    new_plugins = []
    plugin_paths = []
    for path in paths:
        if os.path.isdir(path):
            plugin_paths.extend(glob.glob(os.path.join(path, "*.py")))
        else:
            plugin_paths.append(path)
    for plugin_path in plugin_paths:
        abspath = os.path.abspath(plugin_path)
        for plugin in load(abspath):
            # ensure plugins are unique to avoid duplicate execution, which
            # can happen if, for example, a third-party plugin loads a
            # built-in plugin, which will cause it to appear in the list
            # returned by load() above
            plugin_already_loaded = any(
                existing_plugin.__module__ == plugin.__module__ and existing_plugin.__name__ == plugin.__name__
                for existing_plugin in plugins
            )
            if not plugin_already_loaded:
                plugins.append(plugin)
                new_plugins.append(plugin)
    return new_plugins
