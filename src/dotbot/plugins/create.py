import os
from typing import Any

from dotbot.plugin import Plugin


class Create(Plugin):
    """
    Create empty paths.
    """

    _directive = "create"

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, data: Any) -> bool:
        if directive != self._directive:
            msg = f"Create cannot handle directive {directive}"
            raise ValueError(msg)
        return self._process_paths(data)

    def _process_paths(self, paths: Any) -> bool:
        success = True
        defaults = self._context.defaults().get("create", {})
        for key in paths:
            path = os.path.abspath(os.path.expandvars(os.path.expanduser(key)))
            mode = defaults.get("mode", 0o777)  # same as the default for os.makedirs
            if isinstance(paths, dict):
                options = paths[key]
                if options:
                    mode = options.get("mode", mode)
            success &= self._create(path, mode)
        if success:
            self._log.info("All paths have been set up")
        else:
            self._log.error("Some paths were not successfully set up")
        return success

    def _exists(self, path: str) -> bool:
        """
        Returns true if the path exists.
        """
        path = os.path.expanduser(path)
        return os.path.exists(path)

    def _create(self, path: str, mode: int) -> bool:
        success = True
        if not self._exists(path):
            self._log.debug(f"Trying to create path {path} with mode {mode}")
            try:
                self._log.lowinfo(f"Creating path {path}")
                os.makedirs(path, mode)
                # On Windows, the *mode* argument to `os.makedirs()` is ignored.
                # The mode must be set explicitly in a follow-up call.
                os.chmod(path, mode)
            except OSError:
                self._log.warning(f"Failed to create path {path}")
                success = False
        else:
            self._log.lowinfo(f"Path exists {path}")
        return success
