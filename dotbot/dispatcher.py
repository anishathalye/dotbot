import os
from .plugin import Plugin
from .messenger import Messenger
from .context import Context
from .util import test_success

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
            actions = task
            name = task.get('task', None)
            if name is not None:
                test = task.get('if', None)
                if test is not None and not test_success(test, cwd=self._context.base_directory(), log=self._log):
                    self._log.info('Skipping task %s' % name)
                    actions = []
                else:
                    actions = task.get('actions', [])
                    if not actions:
                        self._log.info('Task %s has no actions' % name)
                    else:
                        self._log.info('Starting task %s' % name)
            for action in actions:
                if self._only is not None and action not in self._only \
                        or self._skip is not None and action in self._skip:
                    self._log.info('Skipping action %s' % action)
                    continue
                handled = False
                if action == 'defaults':
                    self._context.set_defaults(actions[action]) # replace, not update
                    handled = True
                    # keep going, let other plugins handle this if they want
                for plugin in self._plugins:
                    if plugin.can_handle(action):
                        try:
                            success &= plugin.handle(action, actions[action])
                            handled = True
                        except Exception as err:
                            self._log.error(
                                'An error was encountered while executing action %s' %
                                action)
                if not handled:
                    success = False
                    self._log.error('Action %s not handled' % action)
            if name and actions:
                self._log.info('Task %s completed' % name)
        return success

    def _load_plugins(self):
        self._plugins = [plugin(self._context)
            for plugin in Plugin.__subclasses__()]

class DispatchError(Exception):
    pass
