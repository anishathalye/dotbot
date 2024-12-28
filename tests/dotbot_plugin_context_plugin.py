# https://github.com/anishathalye/dotbot/issues/339
# plugins should be able to instantiate a Dispatcher with all the plugins

from typing import Any

import dotbot
from dotbot.dispatcher import Dispatcher


class Dispatch(dotbot.Plugin):
    def can_handle(self, directive: str) -> bool:
        return directive == "dispatch"

    def handle(self, directive: str, data: Any) -> bool:
        if directive != "dispatch":
            msg = f"Dispatch cannot handle directive {directive}"
            raise ValueError(msg)
        dispatcher = Dispatcher(
            base_directory=self._context.base_directory(),
            options=self._context.options(),
            plugins=self._context.plugins(),
        )
        return dispatcher.dispatch(data)
