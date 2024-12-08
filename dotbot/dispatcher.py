import os
from argparse import Namespace

from .context import Context
from .messenger import Messenger
from .plugin import Plugin

# Before b5499c7dc5b300462f3ce1c2a3d9b7a76233b39b, Dispatcher auto-loaded all
# plugins, but after that change, plugins are passed in explicitly (and loaded
# in cli.py). There are some plugins that rely on the old Dispatcher behavior,
# so this is a workaround for implementing similar functionality: when
# Dispatcher is constructed without an explicit list of plugins, _all_plugins is
# used instead.
_all_plugins = []  # filled in by cli.py


class Dispatcher:
    def __init__(
        self,
        base_directory,
        only=None,
        skip=None,
        exit_on_failure=False,
        options=Namespace(),
        plugins=None,
    ):
        # if the caller wants no plugins, the caller needs to explicitly pass in
        # plugins=[]
        self._log = Messenger()
        self._setup_context(base_directory, options, plugins)
        if plugins is None:
            plugins = _all_plugins
        self._plugins = [plugin(self._context) for plugin in plugins]
        self._only = only
        self._skip = skip
        self._exit = exit_on_failure

    def _setup_context(self, base_directory, options, plugins):
        path = os.path.abspath(os.path.expanduser(base_directory))
        if not os.path.exists(path):
            raise DispatchError("Nonexistent base directory")
        self._context = Context(path, options, plugins)

    def dispatch(self, tasks):
        success = True
        for task in tasks:
            for action in task:
                if (
                    self._only is not None
                    and action not in self._only
                    or self._skip is not None
                    and action in self._skip
                ) and action != "defaults":
                    self._log.info("Skipping action %s" % action)
                    continue
                handled = False
                if action == "defaults":
                    self._context.set_defaults(task[action])  # replace, not update
                    handled = True
                    # keep going, let other plugins handle this if they want
                for plugin in self._plugins:
                    if plugin.can_handle(action):
                        try:
                            local_success = plugin.handle(action, task[action])
                            if not local_success and self._exit:
                                # The action has failed exit
                                self._log.error("Action %s failed" % action)
                                return False
                            success &= local_success
                            handled = True
                        except Exception as err:
                            self._log.error(
                                "An error was encountered while executing action %s" % action
                            )
                            self._log.debug(err)
                            if self._exit:
                                # There was an execption exit
                                return False
                if not handled:
                    success = False
                    self._log.error("Action %s not handled" % action)
                    if self._exit:
                        # Invalid action exit
                        return False
        return success


class DispatchError(Exception):
    pass
