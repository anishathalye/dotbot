import os
import sys
from typing import Callable

from tests.conftest import Dotfiles


def test_clean_default(root: str, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify clean uses default unless overridden."""

    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, ".g"))
    dotfiles.write_config(
        [
            {
                "clean": {
                    "~/nonexistent": {"force": True},
                    "~/": None,
                },
            }
        ]
    )
    run_dotbot()

    assert not os.path.isdir(os.path.join(home, "nonexistent"))
    assert os.path.islink(os.path.join(home, ".g"))


def test_clean_environment_variable_expansion(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify clean expands environment variables."""

    os.symlink(os.path.join(dotfiles.directory, "f"), os.path.join(home, ".f"))
    variable = "$HOME"
    if sys.platform == "win32":
        variable = "$USERPROFILE"
    dotfiles.write_config([{"clean": [variable]}])
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".f"))


def test_clean_missing(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify clean deletes links to missing files."""

    dotfiles.write("f")
    os.symlink(os.path.join(dotfiles.directory, "f"), os.path.join(home, ".f"))
    os.symlink(os.path.join(dotfiles.directory, "g"), os.path.join(home, ".g"))
    dotfiles.write_config([{"clean": ["~"]}])
    run_dotbot()

    assert os.path.islink(os.path.join(home, ".f"))
    assert not os.path.islink(os.path.join(home, ".g"))


def test_clean_nonexistent(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify clean ignores nonexistent directories."""

    dotfiles.write_config([{"clean": ["~", "~/fake"]}])
    run_dotbot()  # Nonexistent directories should not raise exceptions.

    assert not os.path.isdir(os.path.join(home, "fake"))


def test_clean_outside_force(root: str, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify clean forced to remove files linking outside dotfiles directory."""

    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, ".g"))
    dotfiles.write_config([{"clean": {"~/": {"force": True}}}])
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".g"))


def test_clean_outside(home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify clean ignores files linking outside dotfiles directory."""

    os.symlink(os.path.join(dotfiles.directory, "f"), os.path.join(home, ".f"))
    os.symlink(os.path.join(home, "g"), os.path.join(home, ".g"))
    dotfiles.write_config([{"clean": ["~"]}])
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".f"))
    assert os.path.islink(os.path.join(home, ".g"))


def test_clean_recursive_1(root: str, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
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


def test_clean_recursive_2(root: str, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
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


def test_clean_defaults_1(root: str, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that clean doesn't erase non-dotfiles links by default."""

    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, ".g"))
    dotfiles.write_config([{"clean": ["~"]}])
    run_dotbot()

    assert os.path.islink(os.path.join(home, ".g"))


def test_clean_defaults_2(root: str, home: str, dotfiles: Dotfiles, run_dotbot: Callable[..., None]) -> None:
    """Verify that explicit clean defaults override the implicit default."""

    os.symlink(os.path.join(root, "nowhere"), os.path.join(home, ".g"))
    dotfiles.write_config(
        [
            {"defaults": {"clean": {"force": True}}},
            {"clean": ["~"]},
        ]
    )
    run_dotbot()

    assert not os.path.islink(os.path.join(home, ".g"))
