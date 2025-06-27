"""Test plugin that counts how many times it's executed.

This file is used to test that duplicate plugin references
don't cause the plugin to be loaded/executed multiple times.
"""

import os.path
from typing import Any

import dotbot


class Counter(dotbot.Plugin):
    def can_handle(self, directive: str) -> bool:
        return directive == "counter"

    def handle(self, directive: str, _data: Any) -> bool:
        if directive != "counter":
            msg = f"Counter cannot handle directive {directive}"
            raise ValueError(msg)

        counter_file = os.path.abspath(os.path.expanduser("~/counter"))
        if os.path.exists(counter_file):
            with open(counter_file) as f:
                count = int(f.read().strip())
        else:
            count = 0
        count += 1
        with open(counter_file, "w") as f:
            f.write(str(count))
        return True
