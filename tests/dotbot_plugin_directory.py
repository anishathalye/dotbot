"""Test that a plugin can be loaded by directory.

This file is copied to a location with the name "directory.py",
and is then loaded from within the `test_cli.py` code.
"""

import os.path

import dotbot


class Directory(dotbot.Plugin):
    def can_handle(self, directive):
        return directive == "plugin_directory"

    def handle(self, directive, data):
        self._log.debug("Attempting to get options from Context")
        options = self._context.options()
        if len(options.plugin_dirs) != 1:
            self._log.debug(
                "Context.options.plugins length is %i, expected 1" % len(options.plugins)
            )
            return False

        with open(os.path.abspath(os.path.expanduser("~/flag")), "w") as file:
            file.write("directory plugin loading works")
        return True
