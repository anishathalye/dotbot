import os
import glob
import dotbot
from ..util import module

class Plugins(dotbot.Plugin):
    '''
    Plugins configuration
    '''

    _directive = 'plugins'

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('Plugins cannot handle directive %s' % directive)
        return self._process_plugins(data)

    def _process_plugins(self, plugins):
        plugin_dirs = []
        plugin_paths = []
        for plugin in plugins:
            if isinstance(plugin, dict):
                plugin_dirs.append(plugin.get('dir', ''))
            else:
                plugin_paths.append(plugin)
        for directory in plugin_dirs:
            for plugin_path in glob.glob(os.path.join(directory, '*.py')):
                plugin_paths.append(plugin_path)
        for plugin in plugin_paths:
            abspath = os.path.abspath(plugin)
            module.load(abspath)
        return True

# vim: ts=4 sw=4 et
