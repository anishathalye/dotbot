import os
from argparse import Namespace
from pprint import pprint

from .plugin import Plugin
from .messenger import Messenger
from .context import Context
import traceback


class Dispatcher(object):
    """Actually processes the yaml data. Delegates to specialised classes"""
    def __init__(self, base_directory, only=None, skip=None, options=Namespace()):
        self._log = Messenger()
        self._setup_context(base_directory, options)
        self._load_plugins()
        self._only = only
        self._skip = skip

    def _setup_context(self, base_directory, options):
        path = os.path.abspath(os.path.expanduser(base_directory))
        if not os.path.exists(path):
            raise DispatchError('Nonexistent base directory')
        self._context = Context(path, options)

    def dispatch(self, tasks):
        pprint(tasks)
        success = True
        for task in tasks:
            for action in task.keys():
                if (
                    self._only is not None
                    and action not in self._only
                    or self._skip is not None
                    and action in self._skip
                ) and action != "defaults":
                    self._log.info("Skipping action %s" % action)
                    continue
                handled = False
                if action == 'defaults':
                    self._context.set_defaults(task[action])  # replace, not update
                    handled = True
                    # keep going, let other plugins handle this if they want
                for plugin in self._plugins:
                    if plugin.can_handle(action):
                        try:
                            success &= plugin.handle(action, task[action])
                            handled = True
                        except Exception as err:
                            print("failure", err)
                            traceback.print_exception(type(err), err, err.__traceback__)
                            self._log.error('An error was encountered while executing action "%s"' % action)
                            self._log.debug(err)
                if not handled:
                    success = False
                    self._log.error('Action %s not handled' % action)
        return success

    def _load_plugins(self):
        self._plugins = [plugin(self._context) for plugin in Plugin.__subclasses__()]


class DispatchError(Exception):
    pass
