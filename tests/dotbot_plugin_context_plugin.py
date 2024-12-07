# https://github.com/anishathalye/dotbot/issues/339
# plugins should be able to instantiate a Dispatcher with all the plugins

import dotbot
from dotbot.dispatcher import Dispatcher


class Dispatch(dotbot.Plugin):
    def can_handle(self, directive):
        return directive == "dispatch"

    def handle(self, directive, data):
        dispatcher = Dispatcher(
            base_directory=self._context.base_directory(),
            options=self._context.options(),
            plugins=self._context.plugins(),
        )
        return dispatcher.dispatch(data)
