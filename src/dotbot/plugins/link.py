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
        for destination, source in links.items():
            destination = os.path.expandvars(destination)  # noqa: PLW2901
            relative = defaults.get("relative", False)
            # support old "canonicalize-path" key for compatibility
            canonical_path = defaults.get("canonicalize", defaults.get("canonicalize-path", True))
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
                    path, destination, relative=relative, canonical_path=canonical_path, ignore_missing=ignore_missing
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
        if relative:
            source = self._relative_path(source, fullpath)
        if (self._is_link(path) and self._link_destination(path) != source) or (
            self._exists(path) and not self._is_link(path)
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

    def _link(self, source: str, link_name: str, *, relative: bool, canonical_path: bool, ignore_missing: bool) -> bool:
        """
        Links link_name to source.

        Returns true if successfully linked files.
        """
        success = False
        destination = os.path.abspath(os.path.expanduser(link_name))
        base_directory = self._context.base_directory(canonical_path=canonical_path)
        absolute_source = os.path.join(base_directory, source)
        link_name = os.path.normpath(link_name)
        source = self._relative_path(absolute_source, destination) if relative else absolute_source
        if not self._exists(link_name) and self._is_link(link_name) and self._link_destination(link_name) != source:
            self._log.warning(f"Invalid link {link_name} -> {self._link_destination(link_name)}")
        # we need to use absolute_source below because our cwd is the dotfiles
        # directory, and if source is relative, it will be relative to the
        # destination directory
        elif not self._exists(link_name) and (ignore_missing or self._exists(absolute_source)):
            try:
                os.symlink(source, destination)
            except OSError:
                self._log.warning(f"Linking failed {link_name} -> {source}")
            else:
                self._log.lowinfo(f"Creating link {link_name} -> {source}")
                success = True
        elif self._exists(link_name) and not self._is_link(link_name):
            self._log.warning(f"{link_name} already exists but is a regular file or directory")
        elif self._is_link(link_name) and self._link_destination(link_name) != source:
            self._log.warning(f"Incorrect link {link_name} -> {self._link_destination(link_name)}")
        # again, we use absolute_source to check for existence
        elif not self._exists(absolute_source):
            if self._is_link(link_name):
                self._log.warning(f"Nonexistent source {link_name} -> {source}")
            else:
                self._log.warning(f"Nonexistent source for {link_name} : {source}")
        else:
            self._log.lowinfo(f"Link exists {link_name} -> {source}")
            success = True
        return success
