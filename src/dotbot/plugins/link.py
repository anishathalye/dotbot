import glob
import os
import shutil
import sys
from typing import Any, List, Optional, Tuple

from dotbot.plugin import Plugin
from dotbot.util import shell_command
from dotbot.util.common import normslash


class Link(Plugin):
    """
    Symbolically links dotfiles.
    """

    supports_dry_run = True

    _directive = "link"

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, data: Any) -> bool:
        if directive != self._directive:
            msg = f"Link cannot handle directive {directive}"
            raise ValueError(msg)
        return self._process_links(data)

    def _process_links(self, links: Any) -> bool:
        success = True
        defaults = self._context.defaults().get("link", {})

        # Validate the default link type before looping.
        link_type = defaults.get("type", "symlink")
        if link_type not in {"symlink", "hardlink"}:
            self._log.warning(f"The default link type is not recognized: '{link_type}'")
            return False

        for link_name, target in links.items():
            link_name = os.path.expandvars(normslash(link_name))  # noqa: PLW2901
            relative = defaults.get("relative", False)
            # support old "canonicalize-path" key for compatibility
            canonical_path = defaults.get("canonicalize", defaults.get("canonicalize-path", True))
            link_type = defaults.get("type", "symlink")
            force = defaults.get("force", False)
            relink = defaults.get("relink", False)
            create = defaults.get("create", False)
            use_glob = defaults.get("glob", False)
            base_prefix = defaults.get("prefix", "")
            test = defaults.get("if", None)
            ignore_missing = defaults.get("ignore-missing", False)
            exclude_paths = defaults.get("exclude", [])
            if isinstance(target, dict):
                # extended config
                test = target.get("if", test)
                relative = target.get("relative", relative)
                canonical_path = target.get("canonicalize", target.get("canonicalize-path", canonical_path))
                link_type = target.get("type", link_type)
                if link_type not in {"symlink", "hardlink"}:
                    msg = f"The link type is not recognized: '{link_type}'"
                    self._log.warning(msg)
                    success = False
                    continue
                force = target.get("force", force)
                relink = target.get("relink", relink)
                create = target.get("create", create)
                use_glob = target.get("glob", use_glob)
                base_prefix = target.get("prefix", base_prefix)
                ignore_missing = target.get("ignore-missing", ignore_missing)
                exclude_paths = target.get("exclude", exclude_paths)
                path = self._default_target(link_name, target.get("path"))
            else:
                path = self._default_target(link_name, target)
            path = normslash(path)
            if test is not None and not self._test_success(test):
                self._log.info(f"Skipping {link_name}")
                continue
            path = os.path.normpath(os.path.expandvars(os.path.expanduser(path)))
            if use_glob and self._has_glob_chars(path):
                glob_results = self._create_glob_results(path, exclude_paths)
                self._log.debug(f"Globs from '{path}': {glob_results}")
                for glob_full_item in glob_results:
                    # Find common dirname between pattern and the item:
                    glob_dirname = os.path.dirname(os.path.commonprefix([path, glob_full_item]))
                    glob_item = glob_full_item if len(glob_dirname) == 0 else glob_full_item[len(glob_dirname) + 1 :]
                    # Add prefix to basepath, if provided
                    if base_prefix:
                        glob_item = base_prefix + glob_item
                    # where is it going
                    glob_link_name = os.path.join(link_name, glob_item)
                    if create:
                        success &= self._create(glob_link_name)
                    did_delete = False
                    if force or relink:
                        did_delete, delete_success = self._delete(
                            glob_full_item,
                            glob_link_name,
                            relative=relative,
                            canonical_path=canonical_path,
                            force=force,
                        )
                        success &= delete_success
                    success &= self._link(
                        glob_full_item,
                        glob_link_name,
                        relative=relative,
                        canonical_path=canonical_path,
                        ignore_missing=ignore_missing,
                        link_type=link_type,
                        did_delete=did_delete,
                    )
            else:
                if create:
                    success &= self._create(link_name)
                if not ignore_missing and not self._exists(os.path.join(self._context.base_directory(), path)):
                    # we seemingly check this twice (here and in _link) because
                    # if the file doesn't exist and force is True, we don't
                    # want to remove the original (this is tested by
                    # link-force-leaves-when-nonexistent.bash)
                    success = False
                    self._log.warning(f"Nonexistent target {link_name} -> {path}")
                    continue
                did_delete = False
                if force or relink:
                    did_delete, delete_success = self._delete(
                        path, link_name, relative=relative, canonical_path=canonical_path, force=force
                    )
                    success &= delete_success
                success &= self._link(
                    path,
                    link_name,
                    relative=relative,
                    canonical_path=canonical_path,
                    ignore_missing=ignore_missing,
                    link_type=link_type,
                    did_delete=did_delete,
                )
        if success:
            self._log.info("All links have been set up")
        else:
            self._log.error("Some links were not successfully set up")
        return success

    def _test_success(self, command: str) -> bool:
        ret = shell_command(command, cwd=self._context.base_directory())
        if ret != 0:
            self._log.debug(f"Test '{command}' returned false")
        return ret == 0

    def _default_target(self, link_name: str, target: Optional[str]) -> str:
        if target is None:
            basename = os.path.basename(link_name)
            if basename.startswith("."):
                return basename[1:]
            return basename
        return target

    def _has_glob_chars(self, path: str) -> bool:
        return any(i in path for i in "?*[")

    def _glob(self, path: str) -> List[str]:
        """
        Wrap `glob.glob` in a python agnostic way, catching errors in usage.
        """
        found = glob.glob(path, recursive=True)
        # normalize paths to ensure cross-platform compatibility
        found = [os.path.normpath(p) for p in found]
        # if using recursive glob (`**`), filter results to return only files:
        if "**" in path and not path.endswith(str(os.sep)):
            self._log.debug("Excluding directories from recursive glob: " + str(path))
            found = [f for f in found if os.path.isfile(f)]
        # return matched results
        return found

    def _create_glob_results(self, path: str, exclude_paths: List[str]) -> List[str]:
        self._log.debug("Globbing with pattern: " + str(path))
        include = self._glob(path)
        self._log.debug("Glob found : " + str(include))
        # filter out any paths matching the exclude globs:
        exclude = []
        for expat in exclude_paths:
            self._log.debug("Excluding globs with pattern: " + str(expat))
            exclude.extend(self._glob(expat))
        self._log.debug("Excluded globs from '" + path + "': " + str(exclude))
        ret = set(include) - set(exclude)
        return list(ret)

    def _is_link(self, path: str) -> bool:
        """
        Returns true if the path is a symbolic link.
        """
        return os.path.islink(os.path.expanduser(path))

    def _link_target(self, path: str) -> str:
        """
        Returns the target of the symbolic link.
        """
        path = os.path.expanduser(path)
        path = os.readlink(path)
        if sys.platform == "win32" and path.startswith("\\\\?\\"):
            path = path[4:]
        return path

    def _exists(self, path: str) -> bool:
        """
        Returns true if the path exists.
        """
        path = os.path.expanduser(path)
        return os.path.exists(path)

    def _lexists(self, path: str) -> bool:
        """
        Returns true if the path exists (including broken symlinks).
        """
        path = os.path.expanduser(path)
        return os.path.lexists(path)

    def _create(self, path: str) -> bool:
        success = True
        parent = os.path.abspath(os.path.join(os.path.expanduser(path), os.pardir))
        if not self._exists(parent):
            self._log.debug(f"Try to create parent: {parent}")
            if self._context.dry_run():
                self._log.action(f"Would create directory {parent}")
                return True
            try:
                os.makedirs(parent)
            except OSError:
                self._log.warning(f"Failed to create directory {parent}")
                success = False
            else:
                self._log.action(f"Creating directory {parent}")
        return success

    def _delete(
        self, target: str, path: str, *, relative: bool, canonical_path: bool, force: bool
    ) -> Tuple[bool, bool]:
        success = True
        removed = False
        target = os.path.join(self._context.base_directory(canonical_path=canonical_path), target)
        fullpath = os.path.abspath(os.path.expanduser(path))
        if self._exists(path) and not self._is_link(path) and os.path.realpath(fullpath) == target:
            # Special case: The path is not a symlink but resolves to the target anyway.
            # Deleting the path would actually delete the target.
            # This may happen if a parent directory is a symlink.
            self._log.warning(f"{path} appears to be the same file as {target}.")
            return False, False
        if relative:
            target = self._relative_path(target, fullpath)
        if (self._is_link(path) and self._link_target(path) != target) or (
            self._lexists(path) and not self._is_link(path)
        ):
            if self._context.dry_run():
                self._log.action(f"Would remove {path}")
                removed = True
            else:
                try:
                    if os.path.islink(fullpath):
                        os.unlink(fullpath)
                        removed = True
                    elif force:
                        if os.path.isdir(fullpath):
                            shutil.rmtree(fullpath)
                            removed = True
                        else:
                            os.remove(fullpath)
                            removed = True
                except OSError:
                    self._log.warning(f"Failed to remove {path}")
                    success = False
                else:
                    if removed:
                        self._log.action(f"Removing {path}")
        return removed, success

    def _relative_path(self, target: str, link_name: str) -> str:
        """
        Returns the relative path to get to the target file from the
        link location.
        """
        link_dir = os.path.dirname(link_name)
        return os.path.relpath(target, link_dir)

    def _link(
        self,
        target: str,
        link_name: str,
        *,
        relative: bool,
        canonical_path: bool,
        ignore_missing: bool,
        link_type: str,
        did_delete: bool,
    ) -> bool:
        """
        Links link_name to target.

        Returns true if successfully linked files.
        """

        link_path = os.path.abspath(os.path.expanduser(link_name))
        base_directory = self._context.base_directory(canonical_path=canonical_path)
        absolute_target = os.path.join(base_directory, target)
        link_name = os.path.normpath(link_name)
        target_path = self._relative_path(absolute_target, link_path) if relative else absolute_target

        # we need to use absolute_target below because our cwd is the dotfiles
        # directory, and if target_path is relative, it will be relative to the
        # link directory
        if ((not self._lexists(link_name)) or (self._context.dry_run() and did_delete)) and (
            ignore_missing or self._exists(absolute_target)
        ):
            if self._context.dry_run():
                self._log.action(f"Would create {link_type} {link_name} -> {target_path}")
                return True
            try:
                if link_type == "symlink":
                    os.symlink(target_path, link_path)
                else:  # link_type == "hardlink"
                    os.link(absolute_target, link_path)
            except OSError:
                self._log.warning(f"Linking failed {link_name} -> {target_path}")
                return False
            else:
                self._log.action(f"Creating {link_type} {link_name} -> {target_path}")
                return True

        # Failure case: The target doesn't exist
        if not self._exists(absolute_target):
            if self._is_link(link_name):
                self._log.warning(f"Nonexistent target {link_name} -> {target_path}")
            else:
                self._log.warning(f"Nonexistent target for {link_name} : {target_path}")
            return False

        # Failure case: The link name exists and is a symlink
        if self._is_link(link_name):
            if link_type == "symlink":
                if self._link_target(link_name) == target_path:
                    # Idempotent case: The configured symlink already exists
                    self._log.info(f"Link exists {link_name} -> {target_path}")
                    return True

                # The existing symlink isn't pointing at the target.
                # Distinguish between an incorrect symlink and a broken ("invalid") symlink.
                terminology = "Incorrect" if self._exists(link_name) else "Invalid"
                self._log.warning(f"{terminology} link {link_name} -> {self._link_target(link_name)}")
                return False

            self._log.warning(f"{link_name} already exists but is a symbolic link, not a hard link")
            return False

        # Failure case: The link name exists
        if link_type == "hardlink" and os.stat(link_path).st_ino == os.stat(absolute_target).st_ino:
            # Idempotent case: The configured hardlink already exists
            self._log.info(f"Link exists {link_name} -> {target_path}")
            return True

        self._log.warning(f"{link_name} already exists but is a regular file or directory")
        return False
