"""Test that a plugin can be loaded by config file.

This file is copied to a location with the name "config_file.py",
and is then loaded from within the `test_cli.py` code.
"""

import os.path

import dotbot


class ConfigFile(dotbot.Plugin):
    def can_handle(self, directive):
        return directive == "plugin_config_file"

    def handle(self, directive, data):
        with open(os.path.abspath(os.path.expanduser("~/flag")), "w") as file:
            file.write("config file plugin loading works")
        return True
