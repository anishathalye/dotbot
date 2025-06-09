import glob
import os
import shutil
import sys
from typing import Any, List, Optional

from dotbot.plugin import Plugin
from dotbot.util import shell_command


class Link(Plugin):
    """
    Symbolically links dotfiles.
    """

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

        for destination, source in links.items():
            destination = os.path.expandvars(destination)  # noqa: PLW2901
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
            if isinstance(source, dict):
                # extended config
                test = source.get("if", test)
                relative = source.get("relative", relative)
                canonical_path = source.get("canonicalize", source.get("canonicalize-path", canonical_path))
                link_type = source.get("type", link_type)
                if link_type not in {"symlink", "hardlink"}:
                    msg = f"The link type is not recognized: '{link_type}'"
                    self._log.warning(msg)
                    success = False
                    continue
                force = source.get("force", force)
                relink = source.get("relink", relink)
                create = source.get("create", create)
                use_glob = source.get("glob", use_glob)
                base_prefix = source.get("prefix", base_prefix)
                ignore_missing = source.get("ignore-missing", ignore_missing)
                exclude_paths = source.get("exclude", exclude_paths)
                path = self._default_source(destination, source.get("path"))
            else:
                path = self._default_source(destination, source)
            if test is not None and not self._test_success(test):
                self._log.lowinfo(f"Skipping {destination}")
                continue
            path = os.path.normpath(os.path.expandvars(os.path.expanduser(path)))
            if use_glob and self._has_glob_chars(path):
                glob_results = self._create_glob_results(path, exclude_paths)
                self._log.lowinfo(f"Globs from '{path}': {glob_results}")
                for glob_full_item in glob_results:
                    # Find common dirname between pattern and the item:
                    glob_dirname = os.path.dirname(os.path.commonprefix([path, glob_full_item]))
                    glob_item = glob_full_item if len(glob_dirname) == 0 else glob_full_item[len(glob_dirname) + 1 :]
                    # Add prefix to basepath, if provided
                    if base_prefix:
                        glob_item = base_prefix + glob_item
                    # where is it going
                    glob_link_destination = os.path.join(destination, glob_item)
                    if create:
                        success &= self._create(glob_link_destination)
                    if force or relink:
                        success &= self._delete(
                            glob_full_item,
                            glob_link_destination,
                            relative=relative,
                            canonical_path=canonical_path,
                            force=force,
                        )
                    success &= self._link(
                        glob_full_item,
                        glob_link_destination,
                        relative=relative,
                        canonical_path=canonical_path,
                        ignore_missing=ignore_missing,
                        link_type=link_type,
                    )
            else:
                if create:
                    success &= self._create(destination)
                if not ignore_missing and not self._exists(os.path.join(self._context.base_directory(), path)):
                    # we seemingly check this twice (here and in _link) because
                    # if the file doesn't exist and force is True, we don't
                    # want to remove the original (this is tested by
                    # link-force-leaves-when-nonexistent.bash)
                    success = False
                    self._log.warning(f"Nonexistent source {destination} -> {path}")
                    continue
                if force or relink:
                    success &= self._delete(
                        path, destination, relative=relative, canonical_path=canonical_path, force=force
                    )
                success &= self._link(
                    path,
                    destination,
                    relative=relative,
                    canonical_path=canonical_path,
                    ignore_missing=ignore_missing,
                    link_type=link_type,
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

    def _default_source(self, destination: str, source: Optional[str]) -> str:
        if source is None:
            basename = os.path.basename(destination)
            if basename.startswith("."):
                return basename[1:]
            return basename
        return source

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

    def _link_destination(self, path: str) -> str:
        """
        Returns the destination of the symbolic link.
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
            try:
                os.makedirs(parent)
            except OSError:
                self._log.warning(f"Failed to create directory {parent}")
                success = False
            else:
                self._log.lowinfo(f"Creating directory {parent}")
        return success

    def _delete(self, source: str, path: str, *, relative: bool, canonical_path: bool, force: bool) -> bool:
        success = True
        source = os.path.join(self._context.base_directory(canonical_path=canonical_path), source)
        fullpath = os.path.abspath(os.path.expanduser(path))
        if self._exists(path) and not self._is_link(path) and os.path.realpath(fullpath) == source:
            # Special case: The path is not a symlink but resolves to the source anyway.
            # Deleting the path would actually delete the source.
            # This may happen if a parent directory is a symlink.
            self._log.warning(f"{path} appears to be the same file as {source}.")
            return False
        if relative:
            source = self._relative_path(source, fullpath)
        if (self._is_link(path) and self._link_destination(path) != source) or (
            self._lexists(path) and not self._is_link(path)
        ):
            removed = False
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
                    self._log.lowinfo(f"Removing {path}")
        return success

    def _relative_path(self, source: str, destination: str) -> str:
        """
        Returns the relative path to get to the source file from the
        destination file.
        """
        destination_dir = os.path.dirname(destination)
        return os.path.relpath(source, destination_dir)

    def _link(
        self,
        source: str,
        link_name: str,
        *,
        relative: bool,
        canonical_path: bool,
        ignore_missing: bool,
        link_type: str,
    ) -> bool:
        """
        Links link_name to source.

        Returns true if successfully linked files.
        """

        destination = os.path.abspath(os.path.expanduser(link_name))
        base_directory = self._context.base_directory(canonical_path=canonical_path)
        absolute_source = os.path.join(base_directory, source)
        link_name = os.path.normpath(link_name)
        source = self._relative_path(absolute_source, destination) if relative else absolute_source

        # we need to use absolute_source below because our cwd is the dotfiles
        # directory, and if source is relative, it will be relative to the
        # destination directory
        if not self._lexists(link_name) and (ignore_missing or self._exists(absolute_source)):
            try:
                if link_type == "symlink":
                    os.symlink(source, destination)
                else:  # link_type == "hardlink"
                    os.link(absolute_source, destination)
            except OSError:
                self._log.warning(f"Linking failed {link_name} -> {source}")
                return False
            else:
                self._log.lowinfo(f"Creating {link_type} {link_name} -> {source}")
                return True

        # Failure case: The source doesn't exist
        if not self._exists(absolute_source):
            if self._is_link(link_name):
                self._log.warning(f"Nonexistent source {link_name} -> {source}")
            else:
                self._log.warning(f"Nonexistent source for {link_name} : {source}")
            return False

        # Failure case: The link target exists and is a symlink
        if self._is_link(link_name):
            if link_type == "symlink":
                if self._link_destination(link_name) == source:
                    # Idempotent case: The configured symlink already exists
                    self._log.lowinfo(f"Link exists {link_name} -> {source}")
                    return True

                # The existing symlink isn't pointing at the source.
                # Distinguish between an incorrect symlink and a broken ("invalid") symlink.
                terminology = "Incorrect" if self._exists(link_name) else "Invalid"
                self._log.warning(f"{terminology} link {link_name} -> {self._link_destination(link_name)}")
                return False

            self._log.warning(f"{link_name} already exists but is a symbolic link, not a hard link")
            return False

        # Failure case: The link target exists
        if link_type == "hardlink" and os.stat(destination).st_ino == os.stat(absolute_source).st_ino:
            # Idempotent case: The configured hardlink already exists
            self._log.lowinfo(f"Link exists {link_name} -> {source}")
            return True

        self._log.warning(f"{link_name} already exists but is a regular file or directory")
        return False
