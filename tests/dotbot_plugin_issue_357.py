from typing import Any

from dotbot.plugin import Plugin

# https://github.com/anishathalye/dotbot/issues/357
# if we import from dotbot.plugins, the built-in plugins get executed multiple times


class NoopPlugin(Plugin):
    _directive = "noop"

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, _data: Any) -> bool:
        if directive != self._directive:
            msg = f"NoopPlugin cannot handle directive {directive}"
            raise ValueError(msg)
        return True
