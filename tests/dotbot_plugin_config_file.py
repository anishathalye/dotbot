"""Test that a plugin can be loaded by config file.

This file is copied to a location with the name "config_file.py",
and is then loaded from within the `test_cli.py` code.
"""

import os.path
from typing import Any

import dotbot


class ConfigFile(dotbot.Plugin):
    _directive = "plugin_config_file"

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, _data: Any) -> bool:
        if not self.can_handle(directive):
            msg = f"ConfigFile cannot handle directive {directive}"
            raise ValueError(msg)
        with open(os.path.abspath(os.path.expanduser("~/flag")), "w") as file:
            file.write("config file plugin loading works")
        return True
