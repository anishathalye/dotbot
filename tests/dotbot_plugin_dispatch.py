"""Test that a plugin can call dispatcher for subtasks.

The plugin calls dispatch with his data.
"""

import os.path

import dotbot


class Dispatch(dotbot.Plugin):
    def can_handle(self, directive):
        return directive == "dispatch"

    def handle(self, directive, data):
        dispatcher = dotbot.dispatcher.Dispatcher(self._context.base_directory())
        return dispatcher.dispatch(data)
