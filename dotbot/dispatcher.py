import os
from .plugin import Plugin
from .messenger import Messenger
from .context import Context

class Dispatcher(object):
    def __init__(self, base_directory, only=None, skip=None):
        self._log = Messenger()
        self._setup_context(base_directory)
        self._load_plugins()
        self._only = only
        self._skip = skip

    def _setup_context(self, base_directory):
        path = os.path.abspath(
            os.path.expanduser(base_directory))
        if not os.path.exists(path):
            raise DispatchError('Nonexistent base directory')
        self._context = Context(path)

    def dispatch(self, tasks):
        success = True
        for task in tasks:
            for action in task:
                if self._only is not None and action not in self._only \
                        or self._skip is not None and action in self._skip:
                    self._log.info('Skipping action %s' % action)
                    continue
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
                        except Exception as err:
                            self._log.error(
                                'An error was encountered while executing action %s' %
                                action)
                            self._log.debug(err)
                if not handled:
                    success = False
                    self._log.error('Action %s not handled' % action)
        return success

    def _load_plugins(self):
        self._plugins = [plugin(self._context)
            for plugin in Plugin.__subclasses__()]

class DispatchError(Exception):
    pass
