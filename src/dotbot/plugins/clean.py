import os
import sys
from typing import Any

from dotbot.plugin import Plugin


class Clean(Plugin):
    """
    Cleans broken symbolic links.
    """

    _directive = "clean"

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, data: Any) -> bool:
        if directive != self._directive:
            msg = f"Clean cannot handle directive {directive}"
            raise ValueError(msg)
        return self._process_clean(data)

    def _process_clean(self, targets: Any) -> bool:
        success = True
        defaults = self._context.defaults().get(self._directive, {})
        for target in targets:
            force = defaults.get("force", False)
            recursive = defaults.get("recursive", False)
            if isinstance(targets, dict) and isinstance(targets[target], dict):
                force = targets[target].get("force", force)
                recursive = targets[target].get("recursive", recursive)
            success &= self._clean(target, force=force, recursive=recursive)
        if success:
            self._log.info("All targets have been cleaned")
        else:
            self._log.error("Some targets were not successfully cleaned")
        return success

    def _clean(self, target: str, *, force: bool, recursive: bool) -> bool:
        """
        Cleans all the broken symbolic links in target if they point to
        a subdirectory of the base directory or if forced to clean.
        """
        if not os.path.isdir(os.path.expandvars(os.path.expanduser(target))):
            self._log.debug(f"Ignoring nonexistent directory {target}")
            return True
        for item in os.listdir(os.path.expandvars(os.path.expanduser(target))):
            path = os.path.abspath(os.path.join(os.path.expandvars(os.path.expanduser(target)), item))
            if recursive and os.path.isdir(path):
                # isdir implies not islink -- we don't want to descend into
                # symlinked directories. okay to do a recursive call here
                # because depth should be fairly limited
                self._clean(path, force=force, recursive=recursive)
            if not os.path.exists(path) and os.path.islink(path):
                points_at = os.path.join(os.path.dirname(path), os.readlink(path))
                if sys.platform == "win32" and points_at.startswith("\\\\?\\"):
                    points_at = points_at[4:]
                if self._in_directory(path, self._context.base_directory()) or force:
                    self._log.lowinfo(f"Removing invalid link {path} -> {points_at}")
                    os.remove(path)
                else:
                    self._log.lowinfo(f"Link {path} -> {points_at} not removed.")
        return True

    def _in_directory(self, path: str, directory: str) -> bool:
        """
        Returns true if the path is in the directory.
        """
        directory = os.path.join(os.path.realpath(directory), "")
        path = os.path.realpath(path)
        return os.path.commonprefix([path, directory]) == directory
