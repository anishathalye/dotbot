import filecmp
import fnmatch
import glob
import os
import re
import shutil
import stat

from ..plugin import Plugin
from ..util import shell_command

class Copy(Plugin):
    """
    Copies files.
    """

    # Constants
    _DIRECTIVE = "copy"
    _GLOB_CHARS = r'[*?\[\]]'
    _DEFAULT_DIRECTORY_MODE = 0o777

    _default_cfg = None
    _extended_cfg = None
    _target_destination = ""

    
    def can_handle(self, directive):
        return directive == self._DIRECTIVE

    def handle(self, directive, data):
        if not self.can_handle(directive):
            raise ValueError(f"Copy cannot handle directive {directive}")
        self._default_cfg = self._context.defaults().get(self._DIRECTIVE, {})
        return self._process_copy(data)

    def _get_config(self, key, defaultValue):
        """
        Return configuration for 'key'
        """

        keyValue = self._default_cfg.get(key, defaultValue)
        if isinstance(self._extended_cfg, dict):
            keyValue = self._extended_cfg.get(key, keyValue)

        return keyValue

    def _test_success(self, command):
        """
        Execute a shell command
        """

        ret = shell_command(command, cwd=self._context.base_directory())
        if ret != 0:
            self._log.debug(f"'if' command '{command}' returned non-zero exit code {ret}")

        return ret == 0

    def _normalize_source(self):
        """
        Return a fully expanded absolute source path
        If the source is implied (ie, no 'path' key, and _extended_cfg is not a str type),
        extract the source from the destination
        """

        source = None

        # self._extended_cfg could be:
        # - a dict, which may or may not have a path key, or
        # - a string representing a source file or directory
        if isinstance(self._extended_cfg, dict):
            source = self._get_config("path", None)
        elif isinstance(self._extended_cfg, str):
            source = self._extended_cfg
        else:
            source = os.path.basename(self._target_destination)
            if source.startswith("."):
                source = source[1:]

        source = os.path.normpath(os.path.expandvars(os.path.expanduser(source)))
        source = os.path.join(self._context.base_directory(), source)

        # This should never happen as long as self._context.base_directory() is an absolute path
        if not os.path.isabs(source):
            self._log.error(f"Error: Invalid source path '{source}'")
            raise OSError("Error: Invalid source path")

        return source

    def _normalize_destination(self):
        """
        Return a fully expanded absolute destination path
        """

        destination = os.path.normpath(os.path.expandvars(os.path.expanduser(self._target_destination)))

        if not os.path.isabs(destination):
            self._log.error(f"Error: Invalid destination path '{destination}'")
            raise OSError("Error: Invalid destination path")

        return destination

    def _contains_glob_chars(self, path):
        """
        Test if the path contains shell glob characters?
        """

        pattern = re.compile(self._GLOB_CHARS)
        return bool(pattern.search(path))

    def _extract_root_from_glob(self, path):
        """
        Extract the root directory from a glob pattern
        """

        glob_chars = self._GLOB_CHARS

        index = min([path.find(char) for char in glob_chars if char in path])
        if index != -1:
            path = path[:index]

        return os.path.normpath(path)

    def _remove_root(self, root, path):
        """
        Remove the root from a path if it's a prefix
        """

        if path.startswith(root):
            return path[len(root):].lstrip(os.path.sep)

        return path

    def _cleanup_backup_extension(self, backup):
        """
        Validate/set the optional backup extension
        """

        if backup:
            if type(backup) == bool:
                backup = "BAK"
            elif type(backup) == str:
                if "/" in backup or ".." in backup:
                    self._log.error(f"Invalid backup extension '{backup}'")
                    raise Exception("Bad extension")
                if backup.startswith("."):
                    backup = backup[1:]
        
        return backup

    def _get_copy_paths(self, prefix=""):
        """
        Returns a list of source path:destination path pairs, handling globbing or directory traversal as needed.
        """

        source = self._normalize_source()
        destination = self._normalize_destination()
        pathlist =[]

        if os.path.isdir(source):
            # Find all files in the directory tree rooted at `source`
            for root, _, files in os.walk(source):
                rel_path = os.path.relpath(root, source)
                dst_root = os.path.abspath(os.path.join(destination, rel_path))
                for file in files:
                    pathlist.append([os.path.abspath(os.path.join(root, file)), os.path.abspath(os.path.join(dst_root, file))])

        elif self._contains_glob_chars(source):
            # Find all files that match the glob in `source`.
            # If we're not prepending a prefix, set include_hidden to get same behavior as os.walk();
            # If we are prepending prefix, do not match hidden files.

            root = self._extract_root_from_glob(source)
            for source_file in glob.glob(source, include_hidden=not prefix, recursive=True):
                if not os.path.isfile(source_file):
                    continue
                dest_file = self._remove_root(root, source_file)
                if prefix:
                    dest_file = prefix + dest_file
                dest = os.path.join(destination, dest_file)
                pathlist.append([source_file, dest])

        else:
            # We just have a [source, destination] pair, return that
            pathlist.append([source, destination])

        return pathlist

    def _filter_excludes(self, paths, exclude_patterns):
        """
        Filter out any source path names that match entries (with wildcards) in exclude_patterns
        """

        if isinstance(exclude_patterns, str):
            exclude_patterns = [ exclude_patterns ]

        full_patterns = []
        for pattern in exclude_patterns:
            new_pattern = os.path.join(self._context.base_directory(), pattern)
            full_patterns.append(new_pattern)

        filtered_paths = []
        for pair in paths:
            matches = any(fnmatch.fnmatch(pair[0], exclude) for exclude in full_patterns)
            if not matches:
                filtered_paths.append(pair)

        return filtered_paths

    def _process_copy(self, copies):
        """
        Process a copy directive
        """


        for self._target_destination, self._extended_cfg in copies.items():

            # Overwrite existing files
            overwrite = self._get_config("overwrite", False)
            # Create any directories that don't exist in destination path
            create = self._get_config("create", False)
            # Filter out path names that match globbing patterns
            exclude_paths = self._get_config("exclude", [])
            # if the shell command returns exit code 0, proceed with copy
            test = self._get_config("if", None)
            # Follow existing destination links
            follow_links = self._get_config("follow-links", True)
            # Force change the file mode
            file_mode = self._get_config("mode", None)
            # Force change directory mode
            dir_mode = self._get_config("dir-mode", None)
            # Copy if content differs
            check_content = self._get_config("check-content", False)
            # Don't fail is source file is missing
            ignore_missing = self._get_config("ignore-missing", False)
            # Don't actually copy files
            dryrun = self._get_config("dryrun", False)
            # Append 'prefix' to the destination path when globbing (disables recursive copying)
            prefix = self._get_config("prefix", "")
            # Make a backup if overwriting destination
            backup = self._get_config("backup", None)

            # Get a valid backup extension, if set
            backup = self._cleanup_backup_extension(backup)   

            paths = self._get_copy_paths(prefix)
            paths = self._filter_excludes(paths, exclude_paths)

            success = True
            for source, destination in paths:
                if not success:
                    break

                self._log.debug(f"Processing {destination}")

                if test is not None and not self._test_success(test):
                    self._log.lowinfo(f"Skipping {destination}")
                    continue

                if not os.path.exists(source):
                    if ignore_missing:
                        self._log.lowinfo(f"Source does not exist, skipping: {source} -> {destination}")
                    else:
                        self._log.lowinfo(f"Error: source does not exist: {source} -> {destination}")
                        success = False
                    continue

                if not os.path.isfile(source):
                    if ignore_missing:
                        self._log.lowinfo(f"Source is not a file, skipping: {source} -> {destination}")
                    else:
                        self._log.lowinfo(f"Error: source is not a file: {source} -> {destination}")
                        success = False
                    continue

                path_has_link = destination != os.path.realpath(destination)
                if path_has_link and not follow_links:
                        self._log.warning(f"Destination {destination} is a link and follow_links is not set, skipping.")
                        success = False
                        continue

                if check_content and os.path.exists(destination) and not filecmp.cmp(source, destination, shallow=False):
                    self._log.debug(f"Content checking enabled and content differs, forcing overwrite")
                    overwrite = True

                if not overwrite and os.path.exists(destination):
                    self._log.lowinfo(f"Destination {destination} exists, skipping")
                    continue

                if dryrun:
                    self._log.info(f"dryrun: copy {source} to {destination}")
                    continue

                ### Changing the filesystem
                if backup and os.path.exists(destination):
                    backup = destination + "." + backup
                    if not self._copyFile(destination, backup):
                        success = False
                        continue

                success &= self._copyFile(source, destination, file_mode, dir_mode, create, backup)

        if success:
            self._log.info(f"All files copied")
        else:
            self._log.error(f"Some files failed to copy")
        return success

    def _update_mode(self, path, mode):
        """
        Updates the file mode for `path` if different
        """

        if not os.path.exists(path):
            return False

        if os.path.islink(path):
           return True

        self._log.debug(f"Updating file mode on {path}: {oct(mode)}")

        file_stat = os.stat(path)
        if stat.S_IMODE(file_stat.st_mode) != mode:
            try:
                os.chmod(path, mode)
            except FileNotFoundError:
                self._log.warning(f"Path does not exist: {path}")
                return False
            except PermissionError:
                self._log.warning(f"Can't change permissions of {path}, permission denied")
                return False
            except OSError as e:
                self._log.warning(f"Error: {e}")
                return False

        return True

    def _create_dirs(self, path, dir_mode=None):
        """
        Create a directory hierarchy.
        Essentially a wrapper around os.makedirs() that sets mode for each directory created
        """

        if not dir_mode:
            dir_mode = self._DEFAULT_DIRECTORY_MODE
        elif isinstance(dir_mode, str):
            try:
                if dir_mode.startswith('0o') or dir_mode.startswith('0'):
                    dir_mode = int(dir_mode, 8)
                else:
                    dir_mode = int(dir_mode)  # Otherwise, treat as a decimal
            except ValueError:
                self._log.error(f"Invalid directory mode: {dir_mode}")
                return False

        parent = os.path.normpath(os.path.dirname(path))

        parts = []
        while True:
            head, tail = os.path.split(parent)
            if head == parent:  # Root reached
                parts.append(head)
                break
            elif tail == parent:  # Root reached
                parts.append(tail)
                break
            else:
                parent = head
                parts.append(tail)
        
        parts.reverse()

        # Create each directory 
        current_path = parts[0]
        for part in parts[1:]:
            current_path = os.path.join(current_path, part)
            if not os.path.exists(current_path):
                try:
                    os.mkdir(current_path, mode=dir_mode)
                except Exception as e:
                    self._log.error(f"Error: mkdir failed with '{e}'")
                    return False

        return True

    def _copyFile(self, source, destination, file_mode=None, dir_mode=None, create=False, backup=None):
        """
        Copies source to dest, optionally changing file mode and creating a backup of existing `destination` file

        Returns true if successfully copied files.  Expects absolute path names for source and destination
        """

        if create and not self._create_dirs(destination, dir_mode):
            return False
        
        try:
            self._log.lowinfo(f"Copying file {source} -> {destination}")
            shutil.copy2(source, destination, follow_symlinks=False)
        except FileNotFoundError:
            if not os.path.exists(source):
                self._log.error(f"The source file '{source}' was not found")
            if not os.path.exists(os.path.dirname(destination)):
                self._log.error(f"The destination path '{os.path.dirname(destination)}' was not found")
            return False
        except PermissionError:
            self._log.error(f"Can't access the source or destination, permission denied")
            return False
        except IsADirectoryError:
            self._log.error(f"The source path is a directory")
            return False
        except shutil.SameFileError:
            self._log.error(f"Source and destination are the same file")
            return False
        except OSError as e:
            self._log.error(f"Error copying file: {e}")
            return False

        # shutil.copy2() also copies metadata.  If the caller wants to override the mode, we do that here.
        if file_mode is None:
            return True

        return self._update_mode(destination, file_mode)
