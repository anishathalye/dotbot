from typing import Any

import dotbot


class Raises(dotbot.Plugin):
    def can_handle(self, directive: str) -> bool:
        return directive == "plugin_raises"

    def handle(self, directive: str, data: Any) -> bool:
        _ = data
        if directive != "plugin_raises":
            msg = f"Raises cannot handle directive {directive}"
            raise ValueError(msg)
        msg = "test exception"
        raise RuntimeError(msg)
