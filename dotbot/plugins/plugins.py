import glob
import os

from ..plugin import Plugin
from ..util import module


class Plugins(Plugin):
    """
    Load plugins from a list of paths.
    """

    _directive = "plugins"
    _has_shown_override_message = False

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError("plugins cannot handle directive %s" % directive)
        return self._process_plugins(data)

    def _process_plugins(self, data):
        success = True
        plugin_paths = []
        for item in data:
            self._log.lowinfo("Loading plugin from %s" % item)

            plugin_path_globs = glob.glob(os.path.join(item, "*.py"))
            if not plugin_path_globs:
                success = False
                self._log.warning("Failed to load plugin from %s" % item)
            else:
                for plugin_path in plugin_path_globs:
                    plugin_paths.append(plugin_path)

        for plugin_path in plugin_paths:
            abspath = os.path.abspath(plugin_path)
            module.load(abspath)

        if success:
            self._log.info("All commands have been executed")
        else:
            self._log.error("Some commands were not successfully executed")
        return success
