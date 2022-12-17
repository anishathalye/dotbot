import glob
import os
import shutil
import sys

from ..plugin import Plugin
from ..util import shell_command


class Link(Plugin):
    """
    Symbolically links dotfiles.
    """

    _directive = "link"

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError("Link cannot handle directive %s" % directive)
        return self._process_links(data)

    def _process_links(self, links):
        success = True
        defaults = self._context.defaults().get("link", {})
        for destination, source in links.items():
            destination = os.path.expandvars(destination)
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
                canonical_path = source.get(
                    "canonicalize", source.get("canonicalize-path", canonical_path)
                )
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
                self._log.lowinfo("Skipping %s" % destination)
                continue
            path = os.path.normpath(os.path.expandvars(os.path.expanduser(path)))
            if use_glob:
                glob_results = self._create_glob_results(path, exclude_paths)
                if len(glob_results) == 0:
                    self._log.warning("Globbing couldn't find anything matching " + str(path))
                    success = False
                    continue
                if len(glob_results) == 1 and destination[-1] == "/":
                    self._log.error("Ambiguous action requested.")
                    self._log.error(
                        "No wildcard in glob, directory use undefined: "
                        + destination
                        + " -> "
                        + str(glob_results)
                    )
                    self._log.warning("Did you want to link the directory or into it?")
                    success = False
                    continue
                elif len(glob_results) == 1 and destination[-1] != "/":
                    # perform a normal link operation
                    if create:
                        success &= self._create(destination)
                    if force or relink:
                        success &= self._delete(path, destination, relative, canonical_path, force)
                    success &= self._link(
                        path, destination, relative, canonical_path, ignore_missing
                    )
                else:
                    self._log.lowinfo("Globs from '" + path + "': " + str(glob_results))
                    for glob_full_item in glob_results:
                        # Find common dirname between pattern and the item:
                        glob_dirname = os.path.dirname(os.path.commonprefix([path, glob_full_item]))
                        glob_item = (
                            glob_full_item
                            if len(glob_dirname) == 0
                            else glob_full_item[len(glob_dirname) + 1 :]
                        )
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
                                relative,
                                canonical_path,
                                force,
                            )
                        success &= self._link(
                            glob_full_item,
                            glob_link_destination,
                            relative,
                            canonical_path,
                            ignore_missing,
                        )
            else:
                if create:
                    success &= self._create(destination)
                if not ignore_missing and not self._exists(
                    os.path.join(self._context.base_directory(), path)
                ):
                    # we seemingly check this twice (here and in _link) because
                    # if the file doesn't exist and force is True, we don't
                    # want to remove the original (this is tested by
                    # link-force-leaves-when-nonexistent.bash)
                    success = False
                    self._log.warning("Nonexistent source %s -> %s" % (destination, path))
                    continue
                if force or relink:
                    success &= self._delete(path, destination, relative, canonical_path, force)
                success &= self._link(path, destination, relative, canonical_path, ignore_missing)
        if success:
            self._log.info("All links have been set up")
        else:
            self._log.error("Some links were not successfully set up")
        return success

    def _test_success(self, command):
        ret = shell_command(command, cwd=self._context.base_directory())
        if ret != 0:
            self._log.debug("Test '%s' returned false" % command)
        return ret == 0

    def _default_source(self, destination, source):
        if source is None:
            basename = os.path.basename(destination)
            if basename.startswith("."):
                return basename[1:]
            else:
                return basename
        else:
            return source

    def _glob(self, path):
        """
        Wrap `glob.glob` in a python agnostic way, catching errors in usage.
        """
        if sys.version_info < (3, 5) and "**" in path:
            self._log.error(
                'Link cannot handle recursive glob ("**") for Python < version 3.5: "%s"' % path
            )
            return []
        # call glob.glob; only python >= 3.5 supports recursive globs
        found = glob.glob(path) if (sys.version_info < (3, 5)) else glob.glob(path, recursive=True)
        # normalize paths to ensure cross-platform compatibility
        found = [os.path.normpath(p) for p in found]
        # if using recursive glob (`**`), filter results to return only files:
        if "**" in path and not path.endswith(str(os.sep)):
            self._log.debug("Excluding directories from recursive glob: " + str(path))
            found = [f for f in found if os.path.isfile(f)]
        # return matched results
        return found

    def _create_glob_results(self, path, exclude_paths):
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

    def _is_link(self, path):
        """
        Returns true if the path is a symbolic link.
        """
        return os.path.islink(os.path.expanduser(path))

    def _link_destination(self, path):
        """
        Returns the destination of the symbolic link.
        """
        path = os.path.expanduser(path)
        path = os.readlink(path)
        if sys.platform[:5] == "win32" and path.startswith("\\\\?\\"):
            path = path[4:]
        return path

    def _exists(self, path):
        """
        Returns true if the path exists.
        """
        path = os.path.expanduser(path)
        return os.path.exists(path)

    def _create(self, path):
        success = True
        parent = os.path.abspath(os.path.join(os.path.expanduser(path), os.pardir))
        if not self._exists(parent):
            self._log.debug("Try to create parent: " + str(parent))
            try:
                os.makedirs(parent)
            except OSError:
                self._log.warning("Failed to create directory %s" % parent)
                success = False
            else:
                self._log.lowinfo("Creating directory %s" % parent)
        return success

    def _delete(self, source, path, relative, canonical_path, force):
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
                self._log.warning("Failed to remove %s" % path)
                success = False
            else:
                if removed:
                    self._log.lowinfo("Removing %s" % path)
        return success

    def _relative_path(self, source, destination):
        """
        Returns the relative path to get to the source file from the
        destination file.
        """
        destination_dir = os.path.dirname(destination)
        return os.path.relpath(source, destination_dir)

    def _link(self, source, link_name, relative, canonical_path, ignore_missing):
        """
        Links link_name to source.

        Returns true if successfully linked files.
        """
        success = False
        destination = os.path.abspath(os.path.expanduser(link_name))
        base_directory = self._context.base_directory(canonical_path=canonical_path)
        absolute_source = os.path.join(base_directory, source)
        link_name = os.path.normpath(link_name)
        if relative:
            source = self._relative_path(absolute_source, destination)
        else:
            source = absolute_source
        if (
            not self._exists(link_name)
            and self._is_link(link_name)
            and self._link_destination(link_name) != source
        ):
            self._log.warning(
                "Invalid link %s -> %s" % (link_name, self._link_destination(link_name))
            )
        # we need to use absolute_source below because our cwd is the dotfiles
        # directory, and if source is relative, it will be relative to the
        # destination directory
        elif not self._exists(link_name) and (ignore_missing or self._exists(absolute_source)):
            try:
                os.symlink(source, destination)
            except OSError:
                self._log.warning("Linking failed %s -> %s" % (link_name, source))
            else:
                self._log.lowinfo("Creating link %s -> %s" % (link_name, source))
                success = True
        elif self._exists(link_name) and not self._is_link(link_name):
            self._log.warning("%s already exists but is a regular file or directory" % link_name)
        elif self._is_link(link_name) and self._link_destination(link_name) != source:
            self._log.warning(
                "Incorrect link %s -> %s" % (link_name, self._link_destination(link_name))
            )
        # again, we use absolute_source to check for existence
        elif not self._exists(absolute_source):
            if self._is_link(link_name):
                self._log.warning("Nonexistent source %s -> %s" % (link_name, source))
            else:
                self._log.warning("Nonexistent source for %s : %s" % (link_name, source))
        else:
            self._log.lowinfo("Link exists %s -> %s" % (link_name, source))
            success = True
        return success
