import os
from typing import Any

import dotbot


class DryRun(dotbot.Plugin):
    """A plugin that is aware of dry-run mode."""

    _directive = "dry_run"
    supports_dry_run = True

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, _directive: str, _data: Any) -> bool:
        if self._context.dry_run():
            self._log.action("Would execute dry run")
        else:
            with open(os.path.abspath(os.path.expanduser("~/flag-dry-run")), "w") as file:
                file.write("Dry run executed")
        return True
