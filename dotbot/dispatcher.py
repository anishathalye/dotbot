import os
from .executor import *
from .messenger import Messenger

class Dispatcher(object):
    PLUGIN_CLASS = Executor
    PLUGIN_DIR = 'dotbot/executor'

    def __init__(self, base_directory):
        self._log = Messenger()
        self._set_base_directory(base_directory)
        self._load_plugins()

    def _set_base_directory(self, base_directory):
        path = os.path.abspath(os.path.realpath(
            os.path.expanduser(base_directory)))
        if os.path.exists(path):
            self._base_directory = path
        else:
            raise DispatchError('Nonexistant base directory')

    def dispatch(self, tasks):
        success = True
        for task in tasks:

            for action in task:
                if action == 'meta':
                    self._handle_metadata(task['meta'])
                    continue
                handled = False
                for plugin in self._plugins:
                    if plugin.can_handle(action):
                        try:
                            success &= plugin.handle(action, task[action])
                            handled = True
                        except Exception:
                            self._log.error(
                                'An error was encountered while executing action %s' %
                                action)
                if not handled:
                    success = False
                    self._log.error('Action %s not handled' % action)
        return success

    def _load_plugins(self):
        self._plugins = [plugin(self._base_directory)
            for plugin in Executor.__subclasses__()]

    def _handle_metadata(self, metadata):
        if 'title' in metadata:
            self._log.warning(metadata['title'])

        if 'description' in metadata:
            self._log.info(' ' + metadata['description'])

class DispatchError(Exception):
    pass
