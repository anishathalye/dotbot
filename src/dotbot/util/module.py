import importlib.util
import os
from types import ModuleType
from typing import List, Type

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
