import glob
import os
from typing import Any

from dotbot.plugin import Plugin
from dotbot.util import module


class Plugins(Plugin):
    """
    Load plugins from a list of paths.
    """

    _directive = "plugins"
    _has_shown_override_message = False

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, data: Any) -> bool:
        if directive != self._directive:
            msg = f"plugins cannot handle directive {directive}"
            raise ValueError(msg)
        return self._process_plugins(data)

    def _process_plugins(self, data: Any) -> bool:
        success = True
        plugin_paths = []
        for item in data:
            self._log.lowinfo(f"Loading plugin from {item}")

            plugin_path_globs = glob.glob(os.path.join(item, "*.py"))
            if not plugin_path_globs:
                success = False
                self._log.warning(f"Failed to load plugin from {item}")
            else:
                plugin_paths = list(plugin_path_globs)

        for plugin_path in plugin_paths:
            abspath = os.path.abspath(plugin_path)
            module.load(abspath)

        if success:
            self._log.info("All commands have been executed")
        else:
            self._log.error("Some commands were not successfully executed")
        return success
