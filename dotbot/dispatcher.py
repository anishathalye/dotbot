import os
from .plugin import Plugin
from .messenger import Messenger
from .context import Context

class Dispatcher(object):
    def __init__(self, base_directory):
        self._log = Messenger()
        self._setup_context(base_directory)
        self._load_plugins()

    def _setup_context(self, base_directory):
        path = os.path.abspath(os.path.realpath(
            os.path.expanduser(base_directory)))
        if not os.path.exists(path):
            raise DispatchError('Nonexistent base directory')
        self._context = Context(path)

    def dispatch(self, tasks):
        success = True
        for task in tasks:
            for action in task:
                handled = False
                if action == 'defaults':
                    self._context.set_defaults(task[action]) # replace, not update
                    handled = True
                    # keep going, let other plugins handle this if they want
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
        self._plugins = [plugin(self._context)
            for plugin in Plugin.__subclasses__()]

class DispatchError(Exception):
    pass
