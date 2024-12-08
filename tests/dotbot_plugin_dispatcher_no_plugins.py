# https://github.com/anishathalye/dotbot/issues/339, https://github.com/anishathalye/dotbot/pull/332
# if plugins instantiate a Dispatcher without explicitly passing in plugins,
# the Dispatcher should have access to all plugins (matching context.plugins())

import dotbot
from dotbot.dispatcher import Dispatcher


class Dispatch(dotbot.Plugin):
    def can_handle(self, directive):
        return directive == "dispatch"

    def handle(self, directive, data):
        dispatcher = Dispatcher(
            base_directory=self._context.base_directory(),
            options=self._context.options(),
        )
        return dispatcher.dispatch(data)
