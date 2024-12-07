import os

from dotbot.plugin import Plugin
from dotbot.plugins import Clean, Create, Link, Shell

# https://github.com/anishathalye/dotbot/issues/357
# if we import from dotbot.plugins, the built-in plugins get executed multiple times


class NoopPlugin(Plugin):
    _directive = "noop"

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        return True
