import os
import sys

import pytest


# Python 2.7 on Windows does not have an `os.symlink()` function.
# PyPy on Windows raises NotImplementedError when `os.symlink()` is called.
# Older Python 3 versions on Windows require admin rights to create symlinks.
#
# In addition, functions like `os.path.realpath()` on Windows Pythons < 3.8
# do not resolve symlinks and directory junctions correctly,
# and `shutil.rmtree()` will fail to delete directory junctions.
#
# For these reasons, if the tests are running on Windows with Python < 3.8
# or with PyPy, the entire link test suite must be skipped.
#
if (
    sys.platform[:5] == "win32"
    and (sys.version_info < (3, 8) or "pypy" in sys.version.lower())
):
    reason = "It is impossible to perform link tests on this platform"
    pytestmark = pytest.mark.skip(reason=reason)


def test_clean_default(root, home, dotfiles, run_dotbot):
    """Verify clean uses default unless overridden."""

    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, ".g"))
    dotfiles.write_config([{
        "clean": {
            "~/nonexistent": {"force": True},
            "~/": None,
        },
    }])
    run_dotbot()

    assert not os.path.isdir(os.path.join(home, "nonexistent"))
    assert os.path.islink(os.path.join(home, ".g"))


def test_clean_environment_variable_expansion(home, dotfiles, run_dotbot):
    """Verify clean expands environment variables."""

    os.symlink(os.path.join(dotfiles.directory, "f"), os.path.join(home, ".f"))
    variable = "$HOME"
    if sys.platform[:5] == "win32":
        variable = "$USERPROFILE"
    dotfiles.write_config([{"clean": [variable]}])
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".f"))


def test_clean_missing(home, dotfiles, run_dotbot):
    """Verify clean deletes links to missing files."""

    dotfiles.write("f")
    os.symlink(os.path.join(dotfiles.directory, "f"), os.path.join(home, ".f"))
    os.symlink(os.path.join(dotfiles.directory, "g"), os.path.join(home, ".g"))
    dotfiles.write_config([{"clean": ["~"]}])
    run_dotbot()

    assert os.path.islink(os.path.join(home, ".f"))
    assert not os.path.islink(os.path.join(home, ".g"))


def test_clean_nonexistent(home, dotfiles, run_dotbot):
    """Verify clean ignores nonexistent directories."""

    dotfiles.write_config([{"clean": ["~", "~/fake"]}])
    run_dotbot()  # Nonexistent directories should not raise exceptions.

    assert not os.path.isdir(os.path.join(home, "fake"))


def test_clean_outside_force(root, home, dotfiles, run_dotbot):
    """Verify clean forced to remove files linking outside dotfiles directory."""

    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, ".g"))
    dotfiles.write_config([{"clean": {"~/": {"force": True}}}])
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".g"))


def test_clean_outside(root, home, dotfiles, run_dotbot):
    """Verify clean ignores files linking outside dotfiles directory."""

    os.symlink(os.path.join(dotfiles.directory, "f"), os.path.join(home, ".f"))
    os.symlink(os.path.join(home, "g"), os.path.join(home, ".g"))
    dotfiles.write_config([{"clean": ["~"]}])
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".f"))
    assert os.path.islink(os.path.join(home, ".g"))


def test_clean_recursive_1(root, home, dotfiles, run_dotbot):
    """Verify clean respects when the recursive directive is off (default)."""

    os.makedirs(os.path.join(home, "a", "b"))
    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, "c"))
    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, "a", "d"))
    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, "a", "b", "e"))
    dotfiles.write_config([{"clean": {"~": {"force": True}}}])
    run_dotbot()

    assert not os.path.islink(os.path.join(home, "c"))
    assert os.path.islink(os.path.join(home, "a", "d"))
    assert os.path.islink(os.path.join(home, "a", "b", "e"))


def test_clean_recursive_2(root, home, dotfiles, run_dotbot):
    """Verify clean respects when the recursive directive is on."""

    os.makedirs(os.path.join(home, "a", "b"))
    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, "c"))
    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, "a", "d"))
    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, "a", "b", "e"))
    dotfiles.write_config([{"clean": {"~": {"force": True, "recursive": True}}}])
    run_dotbot()

    assert not os.path.islink(os.path.join(home, "c"))
    assert not os.path.islink(os.path.join(home, "a", "d"))
    assert not os.path.islink(os.path.join(home, "a", "b", "e"))


def test_clean_defaults_1(root, home, dotfiles, run_dotbot):
    """Verify that clean doesn't erase non-dotfiles links by default."""

    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, ".g"))
    dotfiles.write_config([{"clean": ["~"]}])
    run_dotbot()

    assert os.path.islink(os.path.join(home, ".g"))


def test_clean_defaults_2(root, home, dotfiles, run_dotbot):
    """Verify that explicit clean defaults override the implicit default."""

    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, ".g"))
    dotfiles.write_config([
        {"defaults": {"clean": {"force": True}}},
        {"clean": ["~"]},
    ])
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".g"))
