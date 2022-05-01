"""Test that a plugin can be loaded by filename.

This file is copied to a location with the name "file.py",
and is then loaded from within the `test_cli.py` code.
"""

import os.path

import dotbot


class File(dotbot.Plugin):
    def can_handle(self, directive):
        return directive == "plugin_file"

    def handle(self, directive, data):
        self._log.debug("Attempting to get options from Context")
        options = self._context.options()
        if len(options.plugins) != 1:
            self._log.debug(
                "Context.options.plugins length is %i, expected 1" % len(options.plugins)
            )
            return False
        if not options.plugins[0].endswith("file.py"):
            self._log.debug(
                "Context.options.plugins[0] is %s, expected end with file.py" % options.plugins[0]
            )
            return False

        with open(os.path.abspath(os.path.expanduser("~/flag")), "w") as file:
            file.write("file plugin loading works")
        return True
