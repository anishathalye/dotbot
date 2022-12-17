import ctypes
import json
import os
import shutil
import sys
import tempfile
from shutil import rmtree

import pytest
import yaml

import dotbot.cli

try:
    import builtins
    import unittest.mock as mock
except ImportError:
    # Python 2.7 compatibility
    builtins = None
    import __builtin__
    import mock  # noqa: module not found


def get_long_path(path):
    """Get the long path for a given path."""

    # Do nothing for non-Windows platforms.
    if sys.platform[:5] != "win32":
        return path

    buffer_size = 1000
    buffer = ctypes.create_unicode_buffer(buffer_size)
    get_long_path_name = ctypes.windll.kernel32.GetLongPathNameW
    get_long_path_name(path, buffer, buffer_size)
    return buffer.value


# Python 2.7 compatibility:
# On Linux, Python 2.7's tempfile.TemporaryFile() requires unlink access.
# This list is updated by a tempfile._mkstemp_inner() wrapper,
# and its contents are checked by wrapped functions.
allowed_tempfile_internal_unlink_calls = []


def wrap_function(function, function_path, arg_index, kwarg_key, root):
    def wrapper(*args, **kwargs):
        if kwarg_key in kwargs:
            value = kwargs[kwarg_key]
        else:
            value = args[arg_index]

        # Python 2.7 compatibility:
        # Allow tempfile.TemporaryFile's internal unlink calls to work.
        if value in allowed_tempfile_internal_unlink_calls:
            return function(*args, **kwargs)

        msg = "The '{0}' argument to {1}() must be an absolute path"
        msg = msg.format(kwarg_key, function_path)
        assert value == os.path.abspath(value), msg

        msg = "The '{0}' argument to {1}() must be rooted in {2}"
        msg = msg.format(kwarg_key, function_path, root)
        assert value[: len(str(root))] == str(root), msg

        return function(*args, **kwargs)

    return wrapper


def wrap_open(root):
    try:
        wrapped = getattr(builtins, "open")
    except AttributeError:
        # Python 2.7 compatibility
        wrapped = getattr(__builtin__, "open")

    def wrapper(*args, **kwargs):
        if "file" in kwargs:
            value = kwargs["file"]
        else:
            value = args[0]

        mode = "r"
        if "mode" in kwargs:
            mode = kwargs["mode"]
        elif len(args) >= 2:
            mode = args[1]

        msg = "The 'file' argument to open() must be an absolute path"
        if value != os.devnull and "w" in mode:
            assert value == os.path.abspath(value), msg

        msg = "The 'file' argument to open() must be rooted in {0}"
        msg = msg.format(root)
        if value != os.devnull and "w" in mode:
            assert value[: len(str(root))] == str(root), msg

        return wrapped(*args, **kwargs)

    return wrapper


def rmtree_error_handler(_, path, __):
    # Handle read-only files and directories.
    os.chmod(path, 0o777)
    if os.path.isdir(path):
        rmtree(path)
    else:
        os.unlink(path)


@pytest.fixture(autouse=True, scope="session")
def standardize_tmp():
    r"""Standardize the temporary directory path.

    On MacOS, `/var` is a symlink to `/private/var`.
    This creates issues with link canonicalization and relative link tests,
    so this fixture rewrites environment variables and Python variables
    to ensure the tests work the same as on Linux and Windows.

    On Windows in GitHub CI, the temporary directory may be a short path.
    For example, `C:\Users\RUNNER~1\...` instead of `C:\Users\runneradmin\...`.
    This causes string-based path comparisons to fail.
    """

    tmp = tempfile.gettempdir()
    # MacOS: `/var` is a symlink.
    tmp = os.path.abspath(os.path.realpath(tmp))
    # Windows: The temporary directory may be a short path.
    if sys.platform[:5] == "win32":
        tmp = get_long_path(tmp)
    os.environ["TMP"] = tmp
    os.environ["TEMP"] = tmp
    os.environ["TMPDIR"] = tmp
    tempfile.tempdir = tmp
    yield


@pytest.fixture(autouse=True)
def root(standardize_tmp):
    """Create a temporary directory for the duration of each test."""

    # Reset allowed_tempfile_internal_unlink_calls.
    global allowed_tempfile_internal_unlink_calls
    allowed_tempfile_internal_unlink_calls = []

    # Dotbot changes the current working directory,
    # so this must be reset at the end of each test.
    current_working_directory = os.getcwd()

    # Create an isolated temporary directory from which to operate.
    current_root = tempfile.mkdtemp()

    functions_to_wrap = [
        (os, "chflags", 0, "path"),
        (os, "chmod", 0, "path"),
        (os, "chown", 0, "path"),
        (os, "copy_file_range", 1, "dst"),
        (os, "lchflags", 0, "path"),
        (os, "lchmod", 0, "path"),
        (os, "link", 1, "dst"),
        (os, "makedirs", 0, "name"),
        (os, "mkdir", 0, "path"),
        (os, "mkfifo", 0, "path"),
        (os, "mknod", 0, "path"),
        (os, "remove", 0, "path"),
        (os, "removedirs", 0, "name"),
        (os, "removexattr", 0, "path"),
        (os, "rename", 0, "src"),  # Check both
        (os, "rename", 1, "dst"),
        (os, "renames", 0, "old"),  # Check both
        (os, "renames", 1, "new"),
        (os, "replace", 0, "src"),  # Check both
        (os, "replace", 1, "dst"),
        (os, "rmdir", 0, "path"),
        (os, "setxattr", 0, "path"),
        (os, "splice", 1, "dst"),
        (os, "symlink", 1, "dst"),
        (os, "truncate", 0, "path"),
        (os, "unlink", 0, "path"),
        (os, "utime", 0, "path"),
        (shutil, "chown", 0, "path"),
        (shutil, "copy", 1, "dst"),
        (shutil, "copy2", 1, "dst"),
        (shutil, "copyfile", 1, "dst"),
        (shutil, "copymode", 1, "dst"),
        (shutil, "copystat", 1, "dst"),
        (shutil, "copytree", 1, "dst"),
        (shutil, "make_archive", 0, "base_name"),
        (shutil, "move", 0, "src"),  # Check both
        (shutil, "move", 1, "dst"),
        (shutil, "rmtree", 0, "path"),
        (shutil, "unpack_archive", 1, "extract_dir"),
    ]

    patches = []
    for module, function_name, arg_index, kwarg_key in functions_to_wrap:
        # Skip anything that doesn't exist in this version of Python.
        if not hasattr(module, function_name):
            continue

        # These values must be passed to a separate function
        # to ensure the variable closures work correctly.
        function_path = "{0}.{1}".format(module.__name__, function_name)
        function = getattr(module, function_name)
        wrapped = wrap_function(function, function_path, arg_index, kwarg_key, current_root)
        patches.append(mock.patch(function_path, wrapped))

    # open() must be separately wrapped.
    if builtins is not None:
        function_path = "builtins.open"
    else:
        # Python 2.7 compatibility
        function_path = "__builtin__.open"
    wrapped = wrap_open(current_root)
    patches.append(mock.patch(function_path, wrapped))

    # Block all access to bad functions.
    if hasattr(os, "chroot"):
        patches.append(mock.patch("os.chroot", lambda *_, **__: None))

    # Patch tempfile._mkstemp_inner() so tempfile.TemporaryFile()
    # can unlink files immediately.
    mkstemp_inner = tempfile._mkstemp_inner

    def wrap_mkstemp_inner(*args, **kwargs):
        (fd, name) = mkstemp_inner(*args, **kwargs)
        allowed_tempfile_internal_unlink_calls.append(name)
        return fd, name

    patches.append(mock.patch("tempfile._mkstemp_inner", wrap_mkstemp_inner))

    [patch.start() for patch in patches]
    try:
        yield current_root
    finally:
        [patch.stop() for patch in patches]
        os.chdir(current_working_directory)
        rmtree(current_root, onerror=rmtree_error_handler)


@pytest.fixture
def home(monkeypatch, root):
    """Create a home directory for the duration of the test.

    On *nix, the environment variable "HOME" will be mocked.
    On Windows, the environment variable "USERPROFILE" will be mocked.
    """

    home = os.path.abspath(os.path.join(root, "home/user"))
    os.makedirs(home)
    if sys.platform[:5] == "win32":
        monkeypatch.setenv("USERPROFILE", home)
    else:
        monkeypatch.setenv("HOME", home)
    yield home


class Dotfiles(object):
    """Create and manage a dotfiles directory for a test."""

    def __init__(self, root):
        self.root = root
        self.config = None
        self.config_filename = None
        self.directory = os.path.join(root, "dotfiles")
        os.mkdir(self.directory)

    def makedirs(self, path):
        os.makedirs(os.path.abspath(os.path.join(self.directory, path)))

    def write(self, path, content=""):
        path = os.path.abspath(os.path.join(self.directory, path))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "w") as file:
            file.write(content)

    def write_config(self, config, serializer="yaml", path=None):
        """Write a dotbot config and return the filename."""

        assert serializer in {"json", "yaml"}, "Only json and yaml are supported"
        if serializer == "yaml":
            serialize = yaml.dump
        else:  # serializer == "json"
            serialize = json.dumps

        if path:
            msg = "The config file path must be an absolute path"
            assert path == os.path.abspath(path), msg

            msg = "The config file path must be rooted in {0}"
            msg = msg.format(root)
            assert path[: len(str(root))] == str(root), msg

            self.config_filename = path
        else:
            self.config_filename = os.path.join(self.directory, "install.conf.yaml")
        self.config = config

        with open(self.config_filename, "w") as file:
            file.write(serialize(config))
        return self.config_filename


@pytest.fixture
def dotfiles(root):
    """Create a dotfiles directory."""

    yield Dotfiles(root)


@pytest.fixture
def run_dotbot(dotfiles):
    """Run dotbot.

    When calling `runner()`, only CLI arguments need to be specified.

    If the keyword-only argument *custom* is True
    then the CLI arguments will not be modified,
    and the caller will be responsible for all CLI arguments.
    """

    def runner(*argv, **kwargs):
        argv = ["dotbot"] + list(argv)
        if kwargs.get("custom", False) is not True:
            argv.extend(["-c", dotfiles.config_filename])
        with mock.patch("sys.argv", argv):
            dotbot.cli.main()

    yield runner
