"""Test that a plugin can be loaded by filename.

This file is copied to a location with the name "file.py",
and is then loaded from within the `test_cli.py` code.
"""

import os.path
from typing import Any

import dotbot


class File(dotbot.Plugin):
    def can_handle(self, directive: str) -> bool:
        return directive == "plugin_file"

    def handle(self, directive: str, _data: Any) -> bool:
        if directive != "plugin_file":
            msg = f"File cannot handle directive {directive}"
            raise ValueError(msg)
        self._log.debug("Attempting to get options from Context")
        options = self._context.options()
        if len(options.plugins) != 1:
            self._log.debug(f"Context.options.plugins length is {len(options.plugins)}, expected 1")
            return False
        if not options.plugins[0].endswith("file.py"):
            self._log.debug(f"Context.options.plugins[0] is {options.plugins[0]}, expected end with file.py")
            return False

        with open(os.path.abspath(os.path.expanduser("~/flag")), "w") as file:
            file.write("file plugin loading works")
        return True
