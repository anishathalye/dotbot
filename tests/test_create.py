import os
import stat

import pytest


@pytest.mark.parametrize("directory", ("~/a", "~/b/c"))
def test_directory_creation(home, directory, dotfiles, run_dotbot):
    """Test creating directories, including nested directories."""

    dotfiles.write_config([{"create": [directory]}])
    run_dotbot()

    expanded_directory = os.path.abspath(os.path.expanduser(directory))
    assert os.path.isdir(expanded_directory)
    assert os.stat(expanded_directory).st_mode & 0o777 == 0o777


def test_default_mode(home, dotfiles, run_dotbot):
    """Test creating a directory with an explicit default mode.

    Note: `os.chmod()` on Windows only supports changing write permissions.
    Therefore, this test is restricted to testing read-only access.
    """

    read_only = 0o777 - stat.S_IWUSR - stat.S_IWGRP - stat.S_IWOTH
    config = [{"defaults": {"create": {"mode": read_only}}}, {"create": ["~/a"]}]
    dotfiles.write_config(config)
    run_dotbot()

    directory = os.path.abspath(os.path.expanduser("~/a"))
    assert os.stat(directory).st_mode & stat.S_IWUSR == 0
    assert os.stat(directory).st_mode & stat.S_IWGRP == 0
    assert os.stat(directory).st_mode & stat.S_IWOTH == 0


def test_default_mode_override(home, dotfiles, run_dotbot):
    """Test creating a directory that overrides an explicit default mode.

    Note: `os.chmod()` on Windows only supports changing write permissions.
    Therefore, this test is restricted to testing read-only access.
    """

    read_only = 0o777 - stat.S_IWUSR - stat.S_IWGRP - stat.S_IWOTH
    config = [
        {"defaults": {"create": {"mode": read_only}}},
        {"create": {"~/a": {"mode": 0o777}}},
    ]
    dotfiles.write_config(config)
    run_dotbot()

    directory = os.path.abspath(os.path.expanduser("~/a"))
    assert os.stat(directory).st_mode & stat.S_IWUSR == stat.S_IWUSR
    assert os.stat(directory).st_mode & stat.S_IWGRP == stat.S_IWGRP
    assert os.stat(directory).st_mode & stat.S_IWOTH == stat.S_IWOTH
